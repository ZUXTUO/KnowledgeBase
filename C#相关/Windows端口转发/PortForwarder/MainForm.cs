using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Diagnostics;
using System.Drawing;
using System.Linq;
using System.Security.Principal;
using System.Text;
using System.Windows.Forms;

namespace PortForwarder
{
    public partial class MainForm : Form
    {
        // 用于存储要执行的命令行命令
        string m_command = "";

        // 后台工作线程，用于执行耗时操作，避免UI阻塞
        private BackgroundWorker m_bgWorker = null;

        /// <summary>
        /// MainForm 类的构造函数
        /// </summary>
        public MainForm()
        {
            InitializeComponent(); // 初始化窗体组件

            // 初始化后台工作线程
            m_bgWorker = new BackgroundWorker();
            // 注册DoWork事件处理器，用于执行后台任务
            m_bgWorker.DoWork += ListPortForwardRulesThread;
            // 注册RunWorkerCompleted事件处理器，用于后台任务完成后更新UI
            m_bgWorker.RunWorkerCompleted += new RunWorkerCompletedEventHandler(m_bgWorker_RunWorkerCompleted);
        }

        /// <summary>
        /// 确保在UI线程上执行指定的方法，以避免跨线程操作UI控件的异常。
        /// </summary>
        /// <param name="method">要在UI线程上执行的方法。</param>
        protected virtual void ThreadSafe(MethodInvoker method)
        {
            // 检查是否需要通过Invoke来调用方法（即当前线程不是UI线程）
            if (InvokeRequired)
                Invoke(method); // 在UI线程上异步调用方法
            else
                method(); // 直接在当前线程上调用方法（当前线程是UI线程）
        }

        /// <summary>
        /// 后台工作线程完成时触发的事件处理器。
        /// </summary>
        private void m_bgWorker_RunWorkerCompleted(object sender, RunWorkerCompletedEventArgs e)
        {
            // 无论后台任务是否成功，都将状态更新为“准备就绪...”
            UpdateStatus("准备就绪...");
            // 如果任务中发生错误，显示错误信息
            if (e.Error != null)
            {
                MessageBox.Show($"操作失败: {e.Error.Message}", "错误", MessageBoxButtons.OK, MessageBoxIcon.Error);
            }
            // 确保事件处理器被移除，避免重复注册
            // m_bgWorker.DoWork -= ListPortForwardRulesThread; // 此行不应在此处，因为DoWork在构造函数中只注册一次
        }

        /// <summary>
        /// “列出规则”按钮点击事件处理器。
        /// </summary>
        private void buttonList_Click(object sender, EventArgs e)
        {
            ListPortForwardRules(); // 调用方法列出端口转发规则
        }

        /// <summary>
        /// 在后台线程中执行列出端口转发规则的逻辑。
        /// </summary>
        /// <param name="sender">事件发送者。</param>
        /// <param name="e">DoWorkEventArgs 包含后台任务的信息。</param>
        void ListPortForwardRulesThread(object sender, DoWorkEventArgs e)
        {
            try
            {
                // 设置用于列出所有端口转发规则的命令
                m_command = "netsh interface portproxy show all";

                UpdateCommand(m_command); // 更新命令显示框
                UpdateStatus("正在获取当前端口转发规则列表..."); // 更新状态栏

                // 创建一个新的进程来执行netsh命令
                Process netStat = new Process();
                netStat.StartInfo.UseShellExecute = false; // 不使用操作系统的shell来启动进程
                netStat.StartInfo.CreateNoWindow = true; // 不创建新的控制台窗口
                netStat.StartInfo.FileName = @"cmd.exe"; // 指定要执行的程序是cmd.exe
                // 设置传递给cmd.exe的参数，/C表示执行完命令后关闭cmd窗口
                netStat.StartInfo.Arguments = string.Format(@"/C {0}", m_command);
                netStat.StartInfo.RedirectStandardOutput = true; // 重定向标准输出，以便读取命令的输出
                netStat.Start(); // 启动进程
                string output = netStat.StandardOutput.ReadToEnd(); // 读取命令的所有输出

                // 如果输出为空或只包含空白字符，则表示没有设置端口转发规则
                if (IsNullOrWhiteSpace(output) == true)
                {
                    output = "没有设置端口转发规则！"; // 设置友好的提示信息
                }

                UpdateOutput(output); // 更新输出文本框

                // 状态更新已移至 RunWorkerCompleted 事件中
            }
            catch (Exception ex)
            {
                // 捕获并显示执行命令时可能发生的异常
                MessageBox.Show($"执行命令时发生错误: {ex.Message}", "错误", MessageBoxButtons.OK, MessageBoxIcon.Error);
            }
        }

        /// <summary>
        /// 检查给定的字符串是否为 null、空或仅包含空白字符。
        /// </summary>
        /// <param name="value">要检查的字符串。</param>
        /// <returns>如果字符串为 null、空或仅包含空白字符，则返回 true；否则返回 false。</returns>
        public static bool IsNullOrWhiteSpace(string value)
        {
            if (value == null) return true; // 如果字符串为null，则返回true

            // 遍历字符串中的每个字符
            for (int i = 0; i < value.Length; i++)
            {
                // 如果找到任何非空白字符，则返回false
                if (!Char.IsWhiteSpace(value[i])) return false;
            }

            return true; // 如果所有字符都是空白字符，则返回true
        }

        /// <summary>
        /// 启动后台线程以列出端口转发规则。
        /// </summary>
        private void ListPortForwardRules()
        {
            // 检查后台工作线程是否正在运行，如果正在运行则不重复启动
            if (!m_bgWorker.IsBusy)
            {
                m_bgWorker.RunWorkerAsync(); // 异步启动后台任务
            }
            else
            {
                UpdateStatus("后台任务正在运行，请稍候...");
            }
        }

        /// <summary>
        /// 更新输出文本框的内容（线程安全）。
        /// </summary>
        /// <param name="t">要设置的文本内容。</param>
        private void UpdateOutput(string t)
        {
            ThreadSafe(delegate
            {
                richTextBox1.Text = t; // 更新富文本框内容
            });
        }

        /// <summary>
        /// 更新状态栏的文本内容（线程安全）。
        /// </summary>
        /// <param name="t">要设置的文本内容。</param>
        private void UpdateStatus(string t)
        {
            ThreadSafe(delegate
            {
                toolStripStatusLabel.Text = t; // 更新状态栏标签内容
            });
        }

        /// <summary>
        /// 更新命令显示文本框的内容（线程安全）。
        /// </summary>
        /// <param name="t">要设置的文本内容。</param>
        private void UpdateCommand(string t)
        {
            ThreadSafe(delegate
            {
                textBoxCommand.Text = t; // 更新命令文本框内容
            });
        }

        /// <summary>
        /// 窗体加载事件处理器。
        /// </summary>
        private void Form1_Load(object sender, EventArgs e)
        {
            ListPortForwardRules(); // 窗体加载时自动列出端口转发规则
        }

        /// <summary>
        /// 窗体显示事件处理器。
        /// </summary>
        private void Form1_Shown(object sender, EventArgs e)
        {
            // 获取当前Windows用户的身份
            WindowsIdentity identity = WindowsIdentity.GetCurrent();
            // 基于当前身份创建一个WindowsPrincipal对象
            WindowsPrincipal principal = new WindowsPrincipal(identity);
            // 检查当前用户是否属于Administrator角色
            if (!principal.IsInRole(WindowsBuiltInRole.Administrator))
            {
                // 如果不是管理员，则显示警告信息
                MessageBox.Show("您必须以管理员身份运行此应用程序才能添加/删除端口转发规则。", "警告", MessageBoxButtons.OK, MessageBoxIcon.Warning);
            }
        }

        private void labelStatus_Click(object sender, EventArgs e)
        {
            // 此处无具体逻辑，可能用于UI事件绑定
        }

        private void toolStripButtonAddPortForwarder_Click(object sender, EventArgs e)
        {
            // 此处无具体逻辑，可能用于UI事件绑定
        }

        /// <summary>
        /// 工具栏上的“列出端口转发”按钮点击事件处理器。
        /// </summary>
        private void toolStripButtonListPortForwarding_Click(object sender, EventArgs e)
        {
            ListPortForwardRules(); // 调用方法列出端口转发规则
        }

        /// <summary>
        /// 工具栏上的“添加端口转发”按钮点击事件处理器。
        /// </summary>
        private void toolStripButtonAddPortForward_Click(object sender, EventArgs e)
        {
            // 创建并显示添加端口转发规则的对话框
            AddPortForward dlg = new AddPortForward();
            if (dlg.ShowDialog() == System.Windows.Forms.DialogResult.OK) // 如果对话框结果为OK
            {
                // 格式化添加端口转发规则的netsh命令
                m_command = string.Format("netsh interface portproxy add v4tov4 listenport={0} listenaddress={1} connectport={2} connectaddress={3}",
                                          dlg.textBoxSourcePort.Text, dlg.textBoxSourceIP.Text, dlg.textBoxDestPort.Text, dlg.textBoxDestIP.Text);

                UpdateCommand(m_command); // 更新命令显示框
                UpdateStatus("正在添加端口转发规则..."); // 更新状态栏

                // 创建并启动进程来执行添加规则的命令
                Process netStat = new Process();
                netStat.StartInfo.UseShellExecute = false;
                netStat.StartInfo.CreateNoWindow = true;
                netStat.StartInfo.FileName = @"cmd.exe";
                netStat.StartInfo.Arguments = string.Format(@"/C {0}", m_command);
                netStat.StartInfo.RedirectStandardOutput = true;
                netStat.Start();
                string output = netStat.StandardOutput.ReadToEnd(); // 读取命令输出
                netStat.WaitForExit(); // 等待进程退出，确保命令已完成

                UpdateOutput(output); // 更新输出文本框

                UpdateStatus("准备就绪..."); // 更新状态栏

                // 重要：添加规则后刷新列表
                ListPortForwardRules();
            }
        }

        /// <summary>
        /// 工具栏上的“删除端口转发”按钮点击事件处理器。
        /// </summary>
        private void toolStripButtonDeletePortForward_Click(object sender, EventArgs e)
        {
            // 创建并显示删除端口转发规则的对话框
            DeletePortForward dlg = new DeletePortForward();
            if (dlg.ShowDialog() == System.Windows.Forms.DialogResult.OK) // 如果对话框结果为OK
            {
                // 格式化删除端口转发规则的netsh命令
                m_command = string.Format("netsh interface portproxy delete v4tov4 listenport={0} listenaddress={1}",
                                          dlg.textBoxSourcePort.Text, dlg.textBoxSourceIP.Text);

                UpdateCommand(m_command); // 更新命令显示框
                UpdateStatus("正在删除端口转发规则..."); // 更新状态栏

                // 创建并启动进程来执行删除规则的命令
                Process netStat = new Process();
                netStat.StartInfo.UseShellExecute = false;
                netStat.StartInfo.CreateNoWindow = true;
                netStat.StartInfo.FileName = @"cmd.exe";
                netStat.StartInfo.Arguments = string.Format(@"/C {0}", m_command);
                netStat.StartInfo.RedirectStandardOutput = true;
                netStat.Start();
                string output = netStat.StandardOutput.ReadToEnd(); // 读取命令输出
                netStat.WaitForExit(); // 等待进程退出，确保命令已完成

                UpdateOutput(output); // 更新输出文本框

                UpdateStatus("准备就绪..."); // 更新状态栏

                // 重要：删除规则后刷新列表
                ListPortForwardRules();
            }
        }
    }
}
