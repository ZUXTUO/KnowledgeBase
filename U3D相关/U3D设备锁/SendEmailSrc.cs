using System.Net;
using System.Net.Mail;
using System.Text;
using UnityEngine;
public class SendEmailSrc : MonoBehaviour
{
    //发送邮件所用邮箱
    public static string Mail_ = "111111@qq.com";
    //发送邮件所用邮箱的密码 （第三方客户端登录授权码）
    public static string Key_ = "abcdefh";
    //发送到的邮箱地址
    public static string Mail_Feedback = "222222@qq.com";

    /// <summary>
    /// 发送邮件
    /// </summary>
    /// <param name="receivers">收件⼈</param>
    /// <param name="subject">主题</param>
    /// <param name="body">内容</param>
    public static void Send(string receivers, string subject, string body)
    {
        MailMessage message = new MailMessage();
        message.From = new MailAddress(Mail_);//设置发件地址
        message.To.Add(receivers);//添加收件⼈
        //设置标题和内容及其格式
        message.Subject = subject;
        message.Body = body;
        message.SubjectEncoding = Encoding.UTF8;
        message.BodyEncoding = Encoding.UTF8;
        //设置发件服务器
        SmtpClient client = new SmtpClient("smtp.qq.com");
        client.Credentials = new NetworkCredential(Mail_, Key_) as ICredentialsByHost;
        client.SendCompleted += Client_SendCompleted;//异常
        client.Send(message);//发送消息
    }
    /// <summary>
    /// 异常
    /// </summary>
    /// <param name="sender"></param>
    /// <param name="e"></param>
    private static void Client_SendCompleted(object sender, System.ComponentModel.AsyncCompletedEventArgs e)
    {
        bool result = e.Error == null;
        if (!result)
        {
            Debug.LogError(e.Error);
        }
    }

    public void Close()
    {
        this.gameObject.SetActive(false);
    }
}