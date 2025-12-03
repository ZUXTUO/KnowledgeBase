using UnityEditor;
using UnityEditorInternal;
using UnityEngine;

[InitializeOnLoad]
public static class EnableEnterPlayModeOnLoad
{
    private const string PrefKey = "Custom_EnterPlayModeSettings_AutoSet";

    static EnableEnterPlayModeOnLoad()
    {
        // 如果已经设置过，就不再执行
        if (EditorPrefs.GetBool(PrefKey, false))
            return;

        EnableEnterPlayModeSettings();

        // 标记已执行过
        EditorPrefs.SetBool(PrefKey, true);
    }

    private static void EnableEnterPlayModeSettings()
    {
#if UNITY_2019_3_OR_NEWER
        // 打开 Enter Play Mode Settings
        var settings = EditorSettings.enterPlayModeOptionsEnabled;
        if (!settings)
        {
            EditorSettings.enterPlayModeOptionsEnabled = true;
            // 可根据需要定制选项（如关闭 Domain Reload）
            // EditorSettings.enterPlayModeOptions = EnterPlayModeOptions.DisableDomainReload | EnterPlayModeOptions.DisableSceneReload;

            Debug.Log("自动启用了 Enter Play Mode Settings。");
        }
#endif
    }
}