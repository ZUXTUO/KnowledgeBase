using System.Collections.Generic;
using System.IO;
using System.Security.Cryptography;
using System.Text;
using System.Text.RegularExpressions;
using UnityEngine;
public class Test : MonoBehaviour
{
    public static string name = "";//�˺�
    public static string pasd = "";//����
    public static string snum = "";//����
    public static Rect Back, Lindingwindow;//�����С
    public static bool OnWindows = true, OnSign = true;//�Ƿ���ʾ����

    public void OnEnable()
    {
        OnWindows = true; OnSign = true;
    }

    void OnGUI()
    {
        if (OnWindows)
        {
            Lindingwindow = GUI.Window(0, Lindingwindow, Window, "");//���ܽ���
        }
    }

    public static void MainWindows()
    {
        Lindingwindow = new Rect(Screen.width * 0.5f - 500, Screen.height * 0.5f - 350, 1200, 700);
    }

    public static void Window(int ID)
    {
        GUIStyle fontStyle = new GUIStyle();
        fontStyle.fontSize = 40;//����
        fontStyle.normal.textColor = new Color(255, 255, 255);
        GUI.Label(new Rect(50, 120, 1000, 100), "�˺�:", fontStyle);
        GUI.Label(new Rect(50, 250, 1000, 100), "����:", fontStyle);
        GUI.Label(new Rect(50, 380, 1000, 100), "����:", fontStyle);
        name = SystemInfo.deviceUniqueIdentifier;
        name = GUI.TextField(new Rect(170, 120, 1000, 80), name, fontStyle);
        pasd = GUI.TextField(new Rect(170, 250, 1000, 80), pasd, fontStyle);
        snum = GUI.TextField(new Rect(170, 380, 1000, 80), snum, fontStyle);

        GUI.Label(new Rect(100, 490, 1000, 100), "������˿Ⱥ�������룬�˺�ΪΨһ�豸�벻�ɱ����", fontStyle);

        if (GUI.Button(new Rect(500f, 600f, 200f, 70f), "��֤��¼", fontStyle))
        {
            if (name == Decrypt(pasd, snum))
            {
                Debug.Log("��¼�ɹ�");
                OnWindows = false;
                Time.timeScale = 1f;
                Write();
            }
            else
            {
                Debug.Log("��¼ʧ��");
                OnWindows = true;
                Time.timeScale = 0f;
            }
        }
        if (GUI.Button(new Rect(1000f, 600f, 200f, 70f), "����", fontStyle))
        {
            OnWindows = false;
            Time.timeScale = 1;
        }
        if (OnSign)
        {
            if (GUI.Button(new Rect(50f, 600f, 200f, 70f), "�ύ����", fontStyle))
            {
                OnSign = false;
                Encrypt(SystemInfo.deviceUniqueIdentifier);
                Debug.Log("������Ե��û���" + SystemInfo.deviceUniqueIdentifier + "\n��Կ��" + Temp_Key + "\n���ӣ�" + Temp_Graw);
                string email = "��Ϸ�汾��" + Application.version + "\n" + "������Ե��û���" + SystemInfo.deviceUniqueIdentifier + "\n��Կ��" + Temp_Key + "\n���ӣ�" + Temp_Graw;
                SendEmailSrc.Send(SendEmailSrc.Mail_Feedback, "��������", email);
            }
        }
        GUI.DragWindow();//������ק��һ������
    }

    public static string Key_file, Graw_file;

    /// <summary>
    /// ���õ�ַ    Key
    /// </summary>
    public static string Key_filePathStatic()
    {
#if UNITY_EDITOR || UNITY_STANDALONE || UNITY_WSA_10_0
        Key_file = Application.dataPath + "/Save/Key";//PC
#elif UNITY_ANDROID
        Key_file = Application.persistentDataPath + "/Key";//��׿�ֻ�
#elif UNITY_IOS
        Key_file = Application.persistentDataPath + "/Key";//ƻ���ֻ�
# endif
        return Key_file;
    }
    /// <summary>
    /// ���õ�ַ    Graw
    /// </summary>
    public static string Graw_filePathStatic()
    {
#if UNITY_EDITOR || UNITY_STANDALONE || UNITY_WSA_10_0
        Graw_file = Application.dataPath + "/Save/Graw";//PC
#elif UNITY_ANDROID
        Graw_file = Application.persistentDataPath + "/Graw";//��׿�ֻ�
#elif UNITY_IOS
        Graw_file = Application.persistentDataPath + "/Graw";//ƻ���ֻ�
# endif
        return Graw_file;
    }

    /// <summary>
    /// ��ȡKey-����ʾ����
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
                //�������ͨ����֤����߼�
            }
        }
    }
    /// <summary>
    /// ��ȡKey-��ʾ����
    /// </summary>
    public static void Read()
    {
        FileInfo Key_file = new FileInfo(Key_filePathStatic());
        FileInfo Graw_file = new FileInfo(Graw_filePathStatic());
        if (!Key_file.Exists & !Graw_file.Exists)
        {
            OnWindows = true;//�����ڴ浵
            Time.timeScale = 0;
            MainWindows();
        }
        else
        {
            StreamReader Key_streamReader = new StreamReader(Key_filePathStatic());
            StreamReader Graw_streamReader = new StreamReader(Graw_filePathStatic());
            string Key_str = Key_streamReader.ReadToEnd();
            string Graw_str = Graw_streamReader.ReadToEnd();
            Debug.Log("�ۺ����룺" + Key_str + "  " + Graw_str);
            if (SystemInfo.deviceUniqueIdentifier == Decrypt(Key_str, Graw_str))
            {
                //�������ͨ����֤����߼�
                Debug.Log("ƥ��");
                OnWindows = false;
                Time.timeScale = 1;
            }
            else
            {
                Debug.Log("��ƥ��");
                MainWindows();
                Time.timeScale = 0;
            }
        }
    }
    /// <summary>
    /// ��Կд��
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
        //�������ͨ����֤����߼�
    }






    public static string abecedario = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ";
    public static int[] seed;
    public static bool constantSeed;

    public static string Temp_Key, Temp_Graw;
    /// <summary>
    /// ����
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
            //�ַ�ת����
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
    /// ����
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
            //����ת�ַ���
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
        //��ȡָ���ַ������ַ��м���ַ�
        string regex = "(?<=(" + startStr + "))[.\\s\\S]*?(?=(" + endStr + "))";
        Regex rg = new Regex(regex);
        if (string.IsNullOrEmpty(strs))
            return null;
        //��֤strs��������ǲ���ָ���ַ������ַ��м���ַ�
        bool isMatch = Regex.IsMatch(strs, regex);
        if (!isMatch)
            return null;
        //�ҵ�ƥ��ļ��ϣ���matchColĿǰ���ڵ����ݼ�Ϊʫ������
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