using System;
using System.Collections;
using UnityEngine;

public class TimeLock : MonoBehaviour
{
    private DateTime expirationTime;
    private const string ExpirationKey = "StoredExpirationTime";
    private const string LastCheckTimeKey = "LastCheckTime";

    void Start()
    {
        DontDestroyOnLoad(gameObject);

        // 设置到期时间
        expirationTime = new DateTime(2025, 5, 13);//时间锁上锁日期

        // 存储初始的到期时间，如果尚未存储
        if (!PlayerPrefs.HasKey(ExpirationKey))
        {
            PlayerPrefs.SetString(ExpirationKey, expirationTime.ToString("O")); // ISO 8601 格式
            PlayerPrefs.Save();
        }

        // 启动协程
        StartCoroutine(CheckExpirationRoutine());
    }

    private IEnumerator CheckExpirationRoutine()
    {
        while (true)
        {
            CheckExpiration();
            yield return new WaitForSeconds(300); // 每5分钟检测一次
        }
    }

    private void CheckExpiration()
    {
        // 获取当前时间
        DateTime currentTime = DateTime.Now;

        // 检查是否手动修改了系统时间
        if (PlayerPrefs.HasKey(LastCheckTimeKey))
        {
            DateTime lastCheckTime = DateTime.Parse(PlayerPrefs.GetString(LastCheckTimeKey));
            if (currentTime < lastCheckTime)
            {
                Debug.LogError("检测到系统时间被修改，强制退出应用。");
                Application.Quit();
            }
        }

        // 更新最后检查时间
        PlayerPrefs.SetString(LastCheckTimeKey, currentTime.ToString("O"));
        PlayerPrefs.Save();

        // 获取存储的到期时间
        DateTime storedExpirationTime = DateTime.Parse(PlayerPrefs.GetString(ExpirationKey));

        // 检查当前时间是否超过存储的到期时间
        if (currentTime > storedExpirationTime)
        {
            Debug.LogError("应用已过期，强制退出应用。");
            Application.Quit();
        }
    }
}
