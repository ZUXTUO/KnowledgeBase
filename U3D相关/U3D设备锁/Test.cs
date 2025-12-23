using System.Collections.Generic;
using System.IO;
using System.Security.Cryptography;
using System.Text;
using System.Text.RegularExpressions;
using UnityEngine;
public class Test : MonoBehaviour
{
    public static string name = "";//账号
    public static string pasd = "";//密码
    public static string snum = "";//种子
    public static Rect Back, Lindingwindow;//矩阵大小
    public static bool OnWindows = true, OnSign = true;//是否显示窗口

    public void OnEnable()
    {
        OnWindows = true; OnSign = true;
    }

    void OnGUI()
    {
        if (OnWindows)
        {
            Lindingwindow = GUI.Window(0, Lindingwindow, Window, "");//解密界面
        }
    }

    public static void MainWindows()
    {
        Lindingwindow = new Rect(Screen.width * 0.5f - 500, Screen.height * 0.5f - 350, 1200, 700);
    }

    public static void Window(int ID)
    {
        GUIStyle fontStyle = new GUIStyle();
        fontStyle.fontSize = 40;//字体
        fontStyle.normal.textColor = new Color(255, 255, 255);
        GUI.Label(new Rect(50, 120, 1000, 100), "账号:", fontStyle);
        GUI.Label(new Rect(50, 250, 1000, 100), "密码:", fontStyle);
        GUI.Label(new Rect(50, 380, 1000, 100), "种子:", fontStyle);
        name = SystemInfo.deviceUniqueIdentifier;
        name = GUI.TextField(new Rect(170, 120, 1000, 80), name, fontStyle);
        pasd = GUI.TextField(new Rect(170, 250, 1000, 80), pasd, fontStyle);
        snum = GUI.TextField(new Rect(170, 380, 1000, 80), snum, fontStyle);

        GUI.Label(new Rect(100, 490, 1000, 100), "请加入粉丝群后再申请，账号为唯一设备码不可变更。", fontStyle);

        if (GUI.Button(new Rect(500f, 600f, 200f, 70f), "验证登录", fontStyle))
        {
            if (name == Decrypt(pasd, snum))
            {
                Debug.Log("登录成功");
                OnWindows = false;
                Time.timeScale = 1f;
                Write();
            }
            else
            {
                Debug.Log("登录失败");
                OnWindows = true;
                Time.timeScale = 0f;
            }
        }
        if (GUI.Button(new Rect(1000f, 600f, 200f, 70f), "返回", fontStyle))
        {
            OnWindows = false;
            Time.timeScale = 1;
        }
        if (OnSign)
        {
            if (GUI.Button(new Rect(50f, 600f, 200f, 70f), "提交申请", fontStyle))
            {
                OnSign = false;
                Encrypt(SystemInfo.deviceUniqueIdentifier);
                Debug.Log("申请测试的用户：" + SystemInfo.deviceUniqueIdentifier + "\n密钥：" + Temp_Key + "\n种子：" + Temp_Graw);
                string email = "游戏版本：" + Application.version + "\n" + "申请测试的用户：" + SystemInfo.deviceUniqueIdentifier + "\n密钥：" + Temp_Key + "\n种子：" + Temp_Graw;
                SendEmailSrc.Send(SendEmailSrc.Mail_Feedback, "测试申请", email);
            }
        }
        GUI.DragWindow();//可以拖拽的一个窗口
    }

    public static string Key_file, Graw_file;

    /// <summary>
    /// 外置地址    Key
    /// </summary>
    public static string Key_filePathStatic()
    {
#if UNITY_EDITOR || UNITY_STANDALONE || UNITY_WSA_10_0
        Key_file = Application.dataPath + "/Save/Key";//PC
#elif UNITY_ANDROID
        Key_file = Application.persistentDataPath + "/Key";//安卓手机
#elif UNITY_IOS
        Key_file = Application.persistentDataPath + "/Key";//苹果手机
# endif
        return Key_file;
    }
    /// <summary>
    /// 外置地址    Graw
    /// </summary>
    public static string Graw_filePathStatic()
    {
#if UNITY_EDITOR || UNITY_STANDALONE || UNITY_WSA_10_0
        Graw_file = Application.dataPath + "/Save/Graw";//PC
#elif UNITY_ANDROID
        Graw_file = Application.persistentDataPath + "/Graw";//安卓手机
#elif UNITY_IOS
        Graw_file = Application.persistentDataPath + "/Graw";//苹果手机
# endif
        return Graw_file;
    }

    /// <summary>
    /// 读取Key-不显示窗口
    /// </summary>
    public static void Read_NoWindows()
    {
        FileInfo Key_file = new FileInfo(Key_filePathStatic());
        FileInfo Graw_file = new FileInfo(Graw_filePathStatic());
        if (Key_file.Exists & Graw_file.Exists)
        {
            StreamReader Key_streamReader = new StreamReader(Key_filePathStatic());
            StreamReader Graw_streamReader = new StreamReader(Graw_filePathStatic());
            string Key_str = Key_streamReader.ReadToEnd();
            string Graw_str = Graw_streamReader.ReadToEnd();
            if (SystemInfo.deviceUniqueIdentifier == Decrypt(Key_str, Graw_str))
            {
                //这里添加通过验证后的逻辑
            }
        }
    }
    /// <summary>
    /// 读取Key-显示窗口
    /// </summary>
    public static void Read()
    {
        FileInfo Key_file = new FileInfo(Key_filePathStatic());
        FileInfo Graw_file = new FileInfo(Graw_filePathStatic());
        if (!Key_file.Exists & !Graw_file.Exists)
        {
            OnWindows = true;//不存在存档
            Time.timeScale = 0;
            MainWindows();
        }
        else
        {
            StreamReader Key_streamReader = new StreamReader(Key_filePathStatic());
            StreamReader Graw_streamReader = new StreamReader(Graw_filePathStatic());
            string Key_str = Key_streamReader.ReadToEnd();
            string Graw_str = Graw_streamReader.ReadToEnd();
            Debug.Log("综合密码：" + Key_str + "  " + Graw_str);
            if (SystemInfo.deviceUniqueIdentifier == Decrypt(Key_str, Graw_str))
            {
                //这里添加通过验证后的逻辑
                Debug.Log("匹配");
                OnWindows = false;
                Time.timeScale = 1;
            }
            else
            {
                Debug.Log("不匹配");
                MainWindows();
                Time.timeScale = 0;
            }
        }
    }
    /// <summary>
    /// 密钥写入
    /// </summary>
    public static void Write()
    {
        StreamWriter Key_sw = new StreamWriter(Key_filePathStatic());
        Key_sw.Write(pasd);
        Key_sw.Close();
        Key_sw.Dispose();
        StreamWriter Graw_sw = new StreamWriter(Graw_filePathStatic());
        Graw_sw.Write(snum);
        Graw_sw.Close();
        Graw_sw.Dispose();
        //这里添加通过验证后的逻辑
    }






    public static string abecedario = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ";
    public static int[] seed;
    public static bool constantSeed;

    public static string Temp_Key, Temp_Graw;
    /// <summary>
    /// 加密
    /// </summary>
    /// <param name="input"></param>
    /// <returns></returns>
    public static void Encrypt(string input)
    {
        if (PlayerPrefs.GetInt("cSeed") == 1)
        {
            constantSeed = true;
        }
        else
        {
            constantSeed = false;
        }
        char[] chars = input.ToCharArray();
        int[] ids = new int[chars.Length];
        seed = new int[ids.Length];
        int cseed = 0;
        if (constantSeed && PlayerPrefs.GetInt("seed", -1) == -1)
        {
            cseed = UnityEngine.Random.Range(0, abecedario.Length);
            PlayerPrefs.SetInt("seed", cseed);
        }
        else if (constantSeed)
        {
            cseed = PlayerPrefs.GetInt("seed");
        }
        for (int i = 0; i < chars.Length; i++)
        {
            if (constantSeed)
            {
                seed[i] = cseed;
            }
            else
            {
                seed[i] = UnityEngine.Random.Range(0, abecedario.Length);
            }
            //字符转文字
            System.Text.StringBuilder TxtToNum = new System.Text.StringBuilder(chars[i].ToString().Length);
            foreach (char c in chars[i].ToString())
                TxtToNum.Append((c ^ 2).ToString("D5"));
            int Document = int.Parse(TxtToNum.ToString());
            ids[i] = Document + seed[i];

        }

        string output = "";
        for (int i = 0; i < ids.Length; i++)
        {
            output += ids[i].ToString() + abecedario[seed[i]]; ;
        }

        string sdnum = null;
        for (int ad = 0; ad < seed.Length; ad++)
        {
            if (seed[ad].ToString().Length == 1)
            {
                sdnum = sdnum + "0" + seed[ad].ToString();
            }
            else
            {
                sdnum = sdnum + seed[ad].ToString();
            }
        }
        Temp_Key = output;
        Temp_Graw = sdnum;
    }

    /// <summary>
    /// 解密
    /// </summary>
    /// <param name="input"></param>
    /// <returns></returns>
    public static string Decrypt(string input, string sdnum)
    {
        int a = sdnum.Length / 2;
        seed = new int[a];
        int c = 0;
        for (int b = 0; b < a; b++)
        {
            c = b * 2;
            //Debug.Log(c);
            //Debug.Log(sdnum.Substring(c, 2));
            seed[b] = int.Parse(sdnum.Substring(c, 2));
        }

        char[] chars = input.ToCharArray();

        List<int> ids = new List<int>();
        string[] rawOutput = Regex.Split(input, @"\D+");

        for (int i = 0; i < rawOutput.Length; i++)
        {
            int value;
            if (int.TryParse(rawOutput[i], out value))
            {

                ids.Add(value - seed[i]);

            }
        }

        string output = "";
        string Out = "";
        for (int i = 0; i < ids.Count; i++)
        {
            //Debug.Log(ids[i]);
            //数字转字符串
            System.Text.StringBuilder TxtToNum = new System.Text.StringBuilder(ids[i].ToString().Length);
            int val = int.Parse(ids[i].ToString()) ^ 2;
            TxtToNum.Append((char)val);
            Out = TxtToNum.ToString();

            output += Out;
            //output += char.ConvertFromUtf32(ids[i]);
        }
        return output;
    }

    public static List<string> CDE(string strs, string startStr, string endStr)
    {
        List<string> result = new List<string>();
        //获取指定字符两个字符中间的字符
        string regex = "(?<=(" + startStr + "))[.\\s\\S]*?(?=(" + endStr + "))";
        Regex rg = new Regex(regex);
        if (string.IsNullOrEmpty(strs))
            return null;
        //验证strs里的内容是不是指定字符两个字符中间的字符
        bool isMatch = Regex.IsMatch(strs, regex);
        if (!isMatch)
            return null;
        //找到匹配的集合，即matchCol目前存在的内容即为诗词内容
        MatchCollection matchCol = Regex.Matches(strs, regex);
        if (matchCol.Count > 0)
        {
            for (int i = 0; i < matchCol.Count; i++)
            {
                result.Add(matchCol[i].Value);
                //   Debug.Log(matchCol[i].Value);
            }

        }
        return result;
    }




    public static byte[] EncryptAes(string data, byte[] key, out byte[] iv)
    {
        using (var aes = Aes.Create())
        {
            aes.Mode = CipherMode.CBC; // Should ajust depending on what you want to encrypt
            aes.Key = key;
            aes.GenerateIV(); // Ensure we use a new IV for each encryption

            using (var cryptoTransform = aes.CreateEncryptor())
            {
                iv = aes.IV;
                return cryptoTransform.TransformFinalBlock(Encoding.ASCII.GetBytes(data), 0, data.Length);
            }
        }
    }

    public static string DecryptAes(byte[] data, byte[] key, byte[] iv)
    {
        using (var aes = Aes.Create())
        {
            aes.Key = key;
            aes.IV = iv;
            aes.Mode = CipherMode.CBC; // same as for encryption

            using (var cryptoTransform = aes.CreateDecryptor())
            {
                return Encoding.Default.GetString(cryptoTransform.TransformFinalBlock(data, 0, data.Length));
            }
        }
    }
}