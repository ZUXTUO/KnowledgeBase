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

        // ���õ���ʱ��
        expirationTime = new DateTime(2025, 5, 13);//ʱ������������

        // �洢��ʼ�ĵ���ʱ�䣬�����δ�洢
        if (!PlayerPrefs.HasKey(ExpirationKey))
        {
            PlayerPrefs.SetString(ExpirationKey, expirationTime.ToString("O")); // ISO 8601 ��ʽ
            PlayerPrefs.Save();
        }

        // ����Э��
        StartCoroutine(CheckExpirationRoutine());
    }

    private IEnumerator CheckExpirationRoutine()
    {
        while (true)
        {
            CheckExpiration();
            yield return new WaitForSeconds(300); // ÿ5���Ӽ��һ��
        }
    }

    private void CheckExpiration()
    {
        // ��ȡ��ǰʱ��
        DateTime currentTime = DateTime.Now;

        // ����Ƿ��ֶ��޸���ϵͳʱ��
        if (PlayerPrefs.HasKey(LastCheckTimeKey))
        {
            DateTime lastCheckTime = DateTime.Parse(PlayerPrefs.GetString(LastCheckTimeKey));
            if (currentTime < lastCheckTime)
            {
                Debug.LogError("��⵽ϵͳʱ�䱻�޸ģ�ǿ���˳�Ӧ�á�");
                Application.Quit();
            }
        }

        // ���������ʱ��
        PlayerPrefs.SetString(LastCheckTimeKey, currentTime.ToString("O"));
        PlayerPrefs.Save();

        // ��ȡ�洢�ĵ���ʱ��
        DateTime storedExpirationTime = DateTime.Parse(PlayerPrefs.GetString(ExpirationKey));

        // ��鵱ǰʱ���Ƿ񳬹��洢�ĵ���ʱ��
        if (currentTime > storedExpirationTime)
        {
            Debug.LogError("Ӧ���ѹ��ڣ�ǿ���˳�Ӧ�á�");
            Application.Quit();
        }
    }
}
