using System;
using System.Collections.Generic;
using System.IO;
using UnityEngine;
using UnityEditor;
using System.Linq;
using System.Reflection;

public class ProjectHealthChecker : EditorWindow
{
    private Vector2 scrollPosition;
    private Dictionary<string, List<CheckResult>> checkResults = new Dictionary<string, List<CheckResult>>();
    private Dictionary<string, bool> categoryFoldouts = new Dictionary<string, bool>();
    private bool isChecking = false;

    private float musicLengthThreshold = 20f;
    private bool processForceToMono = true;
    private bool processLoadType = true;

    public static float halveRate = 1f;

    [MenuItem("工具/[优化]检查项目优化情况")]
    public static void ShowWindow()
    {
        GetWindow<ProjectHealthChecker>("Project Health Checker");
    }

    private void OnGUI()
    {
        GUILayout.Label("《大氧化》项目健康检查与优化工具 V0.7", EditorStyles.boldLabel);
        EditorGUILayout.Space();

        EditorGUILayout.BeginVertical("box");
        GUILayout.Label("优化设置", EditorStyles.boldLabel);

        GUILayout.Label("音频优化设置", EditorStyles.miniLabel);
        processForceToMono = EditorGUILayout.Toggle("处理Force To Mono（强制单声道）", processForceToMono);
        processLoadType = EditorGUILayout.Toggle("处理Load Type（加载类型）", processLoadType);
        musicLengthThreshold = EditorGUILayout.FloatField("音乐长度阈值（秒）", musicLengthThreshold);
        EditorGUILayout.HelpBox($"长度超过 {musicLengthThreshold} 秒的音频将被设为Streaming模式", MessageType.Info);
        GUILayout.Space(5);

        GUILayout.Label("纹理优化设置", EditorStyles.miniLabel);
        halveRate = EditorGUILayout.Slider("图片压缩率", halveRate, 0.1f, 1.0f);
        EditorGUILayout.HelpBox($"压缩率越低，图片尺寸越小，但可能牺牲清晰度。设置为1.0表示不压缩到更小尺寸，但会应用其他优化。", MessageType.Info);

        EditorGUILayout.EndVertical();
        GUILayout.Space(10);

        if (GUILayout.Button("检查项目健康状况并应用优化", GUILayout.Height(30)))
        {
            CheckProjectHealth();
        }

        EditorGUILayout.Space();

        if (isChecking)
        {
            EditorGUILayout.LabelField("正在检查项目...", EditorStyles.boldLabel);
            return;
        }

        if (checkResults.Count == 0)
        {
            EditorGUILayout.LabelField("点击上方按钮开始检查项目", EditorStyles.centeredGreyMiniLabel);
            return;
        }

        scrollPosition = EditorGUILayout.BeginScrollView(scrollPosition);

        List<string> categoriesToDraw = new List<string>(checkResults.Keys);
        foreach (var category in categoriesToDraw)
        {
            DrawCategorySection(category);
        }

        EditorGUILayout.EndScrollView();
    }

    private void DrawCategorySection(string category)
    {
        if (!categoryFoldouts.ContainsKey(category))
            categoryFoldouts[category] = true;

        if (!checkResults.TryGetValue(category, out List<CheckResult> results))
        {
            return;
        }

        var issueCount = results.Count(r => !r.passed);

        string categoryTitle = $"{category} ({issueCount} 问题)";
        categoryFoldouts[category] = EditorGUILayout.Foldout(categoryFoldouts[category], categoryTitle, true);

        if (!categoryFoldouts[category])
            return;

        EditorGUI.indentLevel++;

        var issuesInThisCategory = results.Where(r => r.canAutoFix && !r.passed).ToList();
        if (issuesInThisCategory.Any())
        {
            if (GUILayout.Button($"批量修复 {category} 中的问题", GUILayout.Height(25)))
            {
                foreach (var result in issuesInThisCategory)
                {
                    result.fixAction?.Invoke();
                }
                CheckProjectHealth();
            }
            EditorGUILayout.Space(5);
        }

        foreach (var result in results)
        {
            if (!result.passed)
            {
                DrawIssueItem(result);
            }
        }

        EditorGUI.indentLevel--;
        EditorGUILayout.Space();
    }

    private void DrawIssueItem(CheckResult result)
    {
        EditorGUILayout.BeginHorizontal();

        EditorGUILayout.BeginVertical();
        EditorGUILayout.LabelField($"⚠️ {result.name}", EditorStyles.boldLabel);
        EditorGUILayout.LabelField(result.description, EditorStyles.wordWrappedLabel);
        if (!string.IsNullOrEmpty(result.details))
        {
            EditorGUILayout.LabelField($"详情: {result.details}", EditorStyles.miniLabel);
        }
        EditorGUILayout.EndVertical();

        if (result.canAutoFix && GUILayout.Button("修复", GUILayout.Width(60), GUILayout.Height(40)))
        {
            result.fixAction?.Invoke();
            CheckProjectHealth();
        }

        EditorGUILayout.EndHorizontal();
        EditorGUILayout.Space(5);
    }

    private void CheckProjectHealth()
    {
        isChecking = true;
        checkResults.Clear();

        try
        {
            CheckEditorSettings();
            CheckAssets();
            CheckMaterials(); // 新增材质检查
            CheckScripts();
        }
        catch (Exception e)
        {
            Debug.LogError($"检查过程中出现错误: {e.Message}");
        }
        finally
        {
            isChecking = false;
            Repaint();
        }
    }

    private void CheckEditorSettings()
    {
        var results = new List<CheckResult>();

#if UNITY_ANDROID
        var androidStrippingLevel = PlayerSettings.GetManagedStrippingLevel(BuildTargetGroup.Android);
        if (androidStrippingLevel == ManagedStrippingLevel.Low || androidStrippingLevel == ManagedStrippingLevel.Disabled)
        {
            results.Add(new CheckResult
            {
                name = "Android ManagedStrippingLevel 设置",
                description = "Android设置中的ManagedStrippingLevel选项不应为Low或者Disabled",
                passed = false,
                canAutoFix = true,
                fixAction = () => {
                    PlayerSettings.SetManagedStrippingLevel(BuildTargetGroup.Android, ManagedStrippingLevel.Medium);
                    Debug.Log("已将 Android ManagedStrippingLevel 设置为 Medium。");
                }
            });
        }
#endif

#if UNITY_IOS
        var iosStrippingLevel = PlayerSettings.GetManagedStrippingLevel(BuildTargetGroup.iOS);
        if (iosStrippingLevel == ManagedStrippingLevel.Low)
        {
            results.Add(new CheckResult
            {
                name = "iOS ManagedStrippingLevel 设置",
                description = "iOS设置中的ManagedStrippingLevel选项不应为Low",
                passed = false,
                canAutoFix = true,
                fixAction = () => {
                    PlayerSettings.SetManagedStrippingLevel(BuildTargetGroup.iOS, ManagedStrippingLevel.Medium);
                    Debug.Log("已将 iOS ManagedStrippingLevel 设置为 Medium。");
                }
            });
        }
#endif

        if (Physics2D.autoSyncTransforms)
        {
            results.Add(new CheckResult
            {
                name = "Physics2D AutoSyncTransforms 设置",
                description = "在Physics2D设置中应关闭AutoSyncTransforms",
                passed = false,
                canAutoFix = true,
                fixAction = () => {
                    Physics2D.autoSyncTransforms = false;
                    Debug.Log("已关闭 Physics2D AutoSyncTransforms。");
                }
            });
        }

        if (Physics.autoSyncTransforms)
        {
            results.Add(new CheckResult
            {
                name = "Physics AutoSyncTransforms 设置",
                description = "在Physics设置中应关闭AutoSyncTransforms",
                passed = false,
                canAutoFix = true,
                fixAction = () => {
                    Physics.autoSyncTransforms = false;
                    Debug.Log("已关闭 Physics AutoSyncTransforms。");
                }
            });
        }

        if (string.IsNullOrEmpty(PlayerSettings.companyName))
        {
            results.Add(new CheckResult
            {
                name = "CompanyName 设置",
                description = "应设置CompanyName",
                passed = false,
                canAutoFix = false,
                details = "请在Player Settings中手动设置Company Name"
            });
        }

#if UNITY_IOS
        if (PlayerSettings.iOS.accelerometerFrequency != iOSAccelerometerFrequency.Disabled)
        {
            results.Add(new CheckResult
            {
                name = "iOS AccelerometerFrequency 设置",
                description = "iOS设置中的AccelerometerFrequency选项应为 Disabled",
                passed = false,
                canAutoFix = true,
                fixAction = () => {
                    PlayerSettings.iOS.accelerometerFrequency = iOSAccelerometerFrequency.Disabled;
                    Debug.Log("已将 iOS AccelerometerFrequency 设置为 Disabled。");
                }
            });
        }
#endif

        if (Directory.Exists(Path.Combine(Application.dataPath, "Resources")))
        {
            results.Add(new CheckResult
            {
                name = "Resources 文件夹使用",
                description = "不建议使用Resources系统来管理asset",
                passed = false,
                canAutoFix = false,
                details = "建议使用Addressables或其他资源管理方案"
            });
        }

        checkResults["EditorSetting"] = results;
    }

    private void CheckAssets()
    {
        CheckTextures();
        CheckAudio();
        CheckFBX();
        CheckMeshes();
        CheckPrefabs();
        CheckShaders();
        CheckVideos();
    }

    private void CheckTextures()
    {
        var results = new List<CheckResult>();
        var textureGuids = AssetDatabase.FindAssets("t:Texture2D");

        foreach (var guid in textureGuids)
        {
            var path = AssetDatabase.GUIDToAssetPath(guid);
            var importer = AssetImporter.GetAtPath(path) as TextureImporter;
            if (importer == null) continue;

            var texture = AssetDatabase.LoadAssetAtPath<Texture2D>(path);
            if (texture == null) continue;

            bool needsFix = false;
            string fixDetails = "";

            if (!IsPowerOfTwo(texture.width) || !IsPowerOfTwo(texture.height))
            {
                results.Add(new CheckResult
                {
                    name = $"纹理尺寸问题: {Path.GetFileName(path)}",
                    description = "纹理资源的大小应该是2的幂次",
                    passed = false,
                    canAutoFix = false,
                    details = $"当前尺寸: {texture.width}x{texture.height}"
                });
                continue;
            }

            GetTextureOriginalSize(importer, out int width, out int height);
            int expectedSize = GetValidTextureSize((int)(Math.Max(width, height) * halveRate));
            bool isPNG = path.EndsWith(".png", StringComparison.OrdinalIgnoreCase) || path.EndsWith(".tga", StringComparison.OrdinalIgnoreCase);

            // 通用设置判断
            if (!importer.sRGBTexture) { needsFix = true; fixDetails += "sRGBTexture未启用; "; }
            if (importer.mipmapEnabled) { needsFix = true; fixDetails += "mipmapEnabled未禁用; "; }
            if (importer.filterMode != FilterMode.Bilinear) { needsFix = true; fixDetails += "filterMode不是Bilinear; "; }
            if (importer.maxTextureSize > expectedSize) { needsFix = true; fixDetails += $"纹理尺寸过大 ({importer.maxTextureSize} > {expectedSize}); "; }
            if (importer.isReadable) { needsFix = true; fixDetails += "读写标志未禁用; "; }
            if (importer.anisoLevel > 1) { needsFix = true; fixDetails += "各向异性过滤级别大于1; "; }
            if (importer.filterMode == FilterMode.Trilinear) { needsFix = true; fixDetails += "过滤模式为Trilinear; "; }
            if (importer.wrapMode == TextureWrapMode.Repeat) { needsFix = true; fixDetails += "Wrap模式为Repeat; "; }

            // 各平台检查
            string[] platformsToCheck = { "Android", "iOS", "Standalone" };
            foreach (var platform in platformsToCheck)
            {
                var ps = importer.GetPlatformTextureSettings(platform);

                TextureImporterFormat expectedFormat;
                if (platform == "Android") expectedFormat = isPNG ? TextureImporterFormat.ASTC_4x4 : TextureImporterFormat.DXT1;
                else if (platform == "iOS") expectedFormat = isPNG ? TextureImporterFormat.ASTC_4x4 : TextureImporterFormat.PVRTC_RGB4;
                else expectedFormat = isPNG ? TextureImporterFormat.DXT5 : TextureImporterFormat.DXT1;

                if (!ps.overridden)
                {
                    needsFix = true;
                    fixDetails += $"{platform}平台未开启Override; ";
                    continue;
                }

                if (ps.format != expectedFormat)
                {
                    needsFix = true;
                    fixDetails += $"{platform}格式不是期望值({ps.format}≠{expectedFormat}); ";
                }

                if (ps.maxTextureSize != expectedSize)
                {
                    needsFix = true;
                    fixDetails += $"{platform}尺寸不一致({ps.maxTextureSize}≠{expectedSize}); ";
                }

                if (ps.compressionQuality != 75)
                {
                    needsFix = true;
                    fixDetails += $"{platform}压缩质量不是75; ";
                }

                if (ps.resizeAlgorithm != TextureResizeAlgorithm.Bilinear)
                {
                    needsFix = true;
                    fixDetails += $"{platform}未使用Bilinear缩放算法; ";
                }
            }

            if (needsFix)
            {
                results.Add(new CheckResult
                {
                    name = $"纹理优化建议: {Path.GetFileName(path)}",
                    description = $"此纹理可进行优化。{fixDetails.Trim()}",
                    passed = false,
                    canAutoFix = true,
                    details = $"原始尺寸: {width}x{height}, 目标尺寸: {expectedSize}x{expectedSize}",
                    fixAction = () =>
                    {
                        try
                        {
                            importer.sRGBTexture = true;
                            importer.mipmapEnabled = false;
                            importer.filterMode = FilterMode.Bilinear;
                            importer.isReadable = false;
                            importer.anisoLevel = 1;
                            importer.wrapMode = TextureWrapMode.Clamp;

                            string[] platformsToOptimize = { "Android", "iOS", "Standalone" };
                            foreach (var platform in platformsToOptimize)
                            {
                                SetTexturePlatformSettings(importer, platform, expectedSize, isPNG);
                            }

                            importer.SaveAndReimport();
                            Debug.Log($"已成功优化纹理: {path}");
                        }
                        catch (Exception ex)
                        {
                            Debug.LogError($"优化纹理 '{path}' 时发生错误: {ex.Message}\n{ex.StackTrace}");
                        }
                    }
                });
            }
        }

        checkResults["Texture"] = results;
    }

    private void CheckAudio()
    {
        var results = new List<CheckResult>();
        var audioGuids = AssetDatabase.FindAssets("t:AudioClip");

        foreach (var guid in audioGuids)
        {
            var path = AssetDatabase.GUIDToAssetPath(guid);
            var importer = AssetImporter.GetAtPath(path) as AudioImporter;
            if (importer == null) continue;

            var clip = AssetDatabase.LoadAssetAtPath<AudioClip>(path);
            if (clip == null) continue;

            bool needsFix = false;
            string fixDetails = "";

            if (processForceToMono && !importer.forceToMono)
            {
                needsFix = true;
                fixDetails += "未启用Force To Mono; ";
            }

            if (processLoadType)
            {
                AudioClipLoadType targetLoadType = clip.length > musicLengthThreshold ? AudioClipLoadType.Streaming : AudioClipLoadType.CompressedInMemory;

                AudioImporterSampleSettings defaultSettings = importer.defaultSampleSettings;
                if (defaultSettings.loadType != targetLoadType)
                {
                    needsFix = true;
                    fixDetails += $"默认Load Type不符 (期望: {targetLoadType}, 当前: {defaultSettings.loadType}); ";
                }

                AudioImporterSampleSettings androidSettings = importer.GetOverrideSampleSettings("Android");
                bool hasAndroidOverride = importer.ContainsSampleSettingsOverride("Android");

                if (clip.length > musicLengthThreshold)
                {
                    if (!hasAndroidOverride || androidSettings.loadType != AudioClipLoadType.Streaming)
                    {
                        needsFix = true;
                        fixDetails += "Android平台Load Type不符 (期望: Streaming); ";
                    }
                }
            }

            if (needsFix)
            {
                results.Add(new CheckResult
                {
                    name = $"音频优化建议: {Path.GetFileName(path)}",
                    description = $"此音频可进行优化。{fixDetails.Trim()}",
                    passed = false,
                    canAutoFix = true,
                    details = $"长度: {clip.length:F2}秒",
                    fixAction = () => {
                        try
                        {
                            bool reimportNeeded = false;

                            if (processForceToMono && !importer.forceToMono)
                            {
                                importer.forceToMono = true;
                                reimportNeeded = true;
                            }

                            if (processLoadType)
                            {
                                AudioClipLoadType targetLoadType = clip.length > musicLengthThreshold ? AudioClipLoadType.Streaming : AudioClipLoadType.CompressedInMemory;

                                AudioImporterSampleSettings defaultSettings = importer.defaultSampleSettings;
                                if (defaultSettings.loadType != targetLoadType)
                                {
                                    defaultSettings.loadType = targetLoadType;
                                    importer.defaultSampleSettings = defaultSettings;
                                    reimportNeeded = true;
                                }

                                AudioImporterSampleSettings androidSettings = importer.GetOverrideSampleSettings("Android");
                                bool hasAndroidOverride = importer.ContainsSampleSettingsOverride("Android");

                                if (clip.length > musicLengthThreshold)
                                {
                                    if (!hasAndroidOverride || androidSettings.loadType != AudioClipLoadType.Streaming)
                                    {
                                        androidSettings.loadType = AudioClipLoadType.Streaming;
                                        importer.SetOverrideSampleSettings("Android", androidSettings);
                                        reimportNeeded = true;
                                    }
                                }
                            }

                            if (reimportNeeded)
                            {
                                importer.SaveAndReimport();
                                Debug.Log($"已成功优化音频: {path}");
                            }
                        }
                        catch (Exception ex)
                        {
                            Debug.LogError($"优化音频 '{path}' 时发生错误: {ex.Message}\n{ex.StackTrace}");
                        }
                    }
                });
            }
        }

        checkResults["Audio"] = results;
    }

    private void CheckFBX()
    {
        var results = new List<CheckResult>();
        var fbxGuids = AssetDatabase.FindAssets("t:Model");

        foreach (var guid in fbxGuids)
        {
            var path = AssetDatabase.GUIDToAssetPath(guid);
            if (!path.ToLower().EndsWith(".fbx")) continue;

            var importer = AssetImporter.GetAtPath(path) as ModelImporter;
            if (importer == null) continue;

            if (importer.isReadable)
            {
                results.Add(new CheckResult
                {
                    name = $"FBX读写标志: {Path.GetFileName(path)}",
                    description = "应禁用FBX资源的读/写标志",
                    passed = false,
                    canAutoFix = true,
                    fixAction = () => {
                        try
                        {
                            importer.isReadable = false;
                            importer.SaveAndReimport();
                            Debug.Log($"已成功禁用FBX读写标志: {path}");
                        }
                        catch (Exception ex)
                        {
                            Debug.LogError($"优化FBX读写标志 '{path}' 时发生错误: {ex.Message}\n{ex.StackTrace}");
                        }
                    }
                });
            }

            if (!importer.optimizeMeshPolygons)
            {
                results.Add(new CheckResult
                {
                    name = $"FBX网格优化: {Path.GetFileName(path)}",
                    description = "应为网格资源启用OptimizeMesh",
                    passed = false,
                    canAutoFix = true,
                    fixAction = () => {
                        try
                        {
                            importer.optimizeMeshPolygons = true;
                            importer.SaveAndReimport();
                            Debug.Log($"已成功启用FBX网格优化: {path}");
                        }
                        catch (Exception ex)
                        {
                            Debug.LogError($"优化FBX网格 '{path}' 时发生错误: {ex.Message}\n{ex.StackTrace}");
                        }
                    }
                });
            }
        }

        checkResults["FBX"] = results;
    }

    private void CheckMeshes()
    {
        var results = new List<CheckResult>();
        var meshGuids = AssetDatabase.FindAssets("t:Mesh");

        foreach (var guid in meshGuids)
        {
            var path = AssetDatabase.GUIDToAssetPath(guid);
            var importer = AssetImporter.GetAtPath(path) as ModelImporter;
            if (importer == null) continue;

            if (importer.isReadable)
            {
                results.Add(new CheckResult
                {
                    name = $"网格读写标志: {Path.GetFileName(path)}",
                    description = "应为网格资源禁用读/写标志",
                    passed = false,
                    canAutoFix = true,
                    fixAction = () => {
                        try
                        {
                            importer.isReadable = false;
                            importer.SaveAndReimport();
                            Debug.Log($"已成功禁用网格读写标志: {path}");
                        }
                        catch (Exception ex)
                        {
                            Debug.LogError($"优化网格读写标志 '{path}' 时发生错误: {ex.Message}\n{ex.StackTrace}");
                        }
                    }
                });
            }
        }

        checkResults["Mesh"] = results;
    }

    private void CheckPrefabs()
    {
        var results = new List<CheckResult>();
        var prefabGuids = AssetDatabase.FindAssets("t:Prefab");

        foreach (var guid in prefabGuids)
        {
            var path = AssetDatabase.GUIDToAssetPath(guid);
            var prefab = AssetDatabase.LoadAssetAtPath<GameObject>(path);
            if (prefab == null) continue;

            var particleSystems = prefab.GetComponentsInChildren<ParticleSystem>();
            foreach (var ps in particleSystems)
            {
                var main = ps.main;
                if (main.maxParticles > 100)
                {
                    results.Add(new CheckResult
                    {
                        name = $"预制件粒子数量: {Path.GetFileName(path)} - {ps.name}",
                        description = "渲染Mesh的粒子系统不宜设置过高的粒子总数",
                        passed = false,
                        canAutoFix = false,
                        details = $"当前最大粒子数: {main.maxParticles}"
                    });
                }

                var emission = ps.emission;
                if (emission.rateOverTime.constant > 50)
                {
                    results.Add(new CheckResult
                    {
                        name = $"预制件粒子发射率: {Path.GetFileName(path)} - {ps.name}",
                        description = "渲染Mesh的粒子系统不宜设置过高的粒子发射速率",
                        passed = false,
                        canAutoFix = false,
                        details = $"当前发射速率: {emission.rateOverTime.constant}"
                    });
                }
            }
        }

        checkResults["Prefab"] = results;
    }

    private void CheckShaders()
    {
        var results = new List<CheckResult>();
        var shaderGuids = AssetDatabase.FindAssets("t:Shader");

        foreach (var guid in shaderGuids)
        {
            var path = AssetDatabase.GUIDToAssetPath(guid);
            var shader = AssetDatabase.LoadAssetAtPath<Shader>(path);
            if (shader == null) continue;

            try
            {
                int passCount = shader.passCount;
                if (passCount > 1)
                {
                    results.Add(new CheckResult
                    {
                        name = $"着色器Pass数量: {Path.GetFileName(path)}",
                        description = $"此着色器包含 {passCount} 个Pass。",
                        passed = false,
                        canAutoFix = false,
                        details = "着色器Pass数量过多可能会影响渲染性能。请检查着色器逻辑是否可简化，或考虑合并Pass。"
                    });
                }
            }
            catch (Exception ex)
            {
                Debug.LogError($"检查着色器 '{path}' 的Pass数量时发生错误: {ex.Message}");
                results.Add(new CheckResult
                {
                    name = $"着色器检查错误: {Path.GetFileName(path)}",
                    description = "检查着色器Pass数量时发生错误。",
                    passed = false,
                    canAutoFix = false,
                    details = $"错误信息: {ex.Message}"
                });
            }
        }

        checkResults["Shader"] = results;
    }

    private void CheckVideos()
    {
        var results = new List<CheckResult>();
        var videoGuids = AssetDatabase.FindAssets("t:VideoClip");

        foreach (var guid in videoGuids)
        {
            string path = AssetDatabase.GUIDToAssetPath(guid);
            if (string.IsNullOrEmpty(path))
            {
                Debug.LogWarning($"找不到资源路径，GUID: {guid}");
                continue;
            }

            var importer = AssetImporter.GetAtPath(path) as VideoClipImporter;
            if (importer == null)
            {
                Debug.LogWarning($"无法获取视频导入器: {path}");
                continue;
            }

            VideoImporterTargetSettings androidSettings = new VideoImporterTargetSettings();
            try
            {
                androidSettings = importer.GetTargetSettings("Android");

                if (androidSettings == null)
                {
                    // 如果设置为 null，说明从未设置过该平台，初始化一个默认设置
                    androidSettings = new VideoImporterTargetSettings
                    {
                        enableTranscoding = false,
                        codec = VideoCodec.Auto,
                        bitrateMode = VideoBitrateMode.Low,
                        spatialQuality = VideoSpatialQuality.LowSpatialQuality,
                        resizeMode = VideoResizeMode.OriginalSize
                    };

                    importer.SetTargetSettings("Android", androidSettings);
                    importer.SaveAndReimport();

                    Debug.LogWarning($"Android 设置为 null，已初始化默认设置: {path}");
                }
            }
            catch (Exception ex)
            {
                Debug.LogWarning($"无法获取 Android 设置: {path}, 原因: {ex.Message}");
                importer.SetTargetSettings("Android", androidSettings);
                continue;
            }

            if (androidSettings == null)
            {
                Debug.LogWarning($"Android 设置为 null: {path}");
                continue;
            }

            bool needsFix = false;
            string fixDetails = "";

            // 检查当前设置
            if (!androidSettings.enableTranscoding)
            {
                needsFix = true;
                fixDetails += "需要开启转码(Transcode); ";
            }
            if (androidSettings.codec != VideoCodec.H264)
            {
                needsFix = true;
                fixDetails += $"编解码器(Codec)不是H.264 (当前: {androidSettings.codec}); ";
            }
            if (androidSettings.bitrateMode != VideoBitrateMode.Medium)
            {
                needsFix = true;
                fixDetails += $"比特率模式(Bitrate Mode)不是中等(Medium) (当前: {androidSettings.bitrateMode}); ";
            }
            if (androidSettings.spatialQuality != VideoSpatialQuality.MediumSpatialQuality)
            {
                needsFix = true;
                fixDetails += $"空间质量(Spatial Quality)不是中等(Medium) (当前: {androidSettings.spatialQuality}); ";
            }

            // 判断是否需要修复
            if (needsFix)
            {
                results.Add(new CheckResult
                {
                    name = $"视频安卓平台优化: {System.IO.Path.GetFileName(path)}",
                    description = "安卓平台视频编码设置不符合标准。",
                    passed = false,
                    canAutoFix = true,
                    details = fixDetails.Trim(),
                    fixAction = () =>
                    {
                        try
                        {
                            var newSettings = new VideoImporterTargetSettings
                            {
                                enableTranscoding = true,
                                codec = VideoCodec.H264,
                                bitrateMode = VideoBitrateMode.Medium,
                                spatialQuality = VideoSpatialQuality.MediumSpatialQuality,
                                resizeMode = VideoResizeMode.OriginalSize
                            };

                            importer.SetTargetSettings("Android", newSettings);
                            importer.SaveAndReimport();
                            Debug.Log($"已成功优化视频安卓平台设置: {path}");
                        }
                        catch (Exception ex)
                        {
                            Debug.LogError($"优化视频 '{path}' 时出错: {ex.Message}\n{ex.StackTrace}");
                        }
                    }
                });
            }
        }

        if (!checkResults.ContainsKey("Video"))
            checkResults["Video"] = new List<CheckResult>();

        checkResults["Video"] = results;
    }

    /// <summary>
    /// 检查所有材质球的Enable GPU Instancing和Double Sided GI设置
    /// </summary>
    private void CheckMaterials()
    {
        var results = new List<CheckResult>();
        var matGuids = AssetDatabase.FindAssets("t:Material");

        foreach (var guid in matGuids)
        {
            var path = AssetDatabase.GUIDToAssetPath(guid);
            var mat = AssetDatabase.LoadAssetAtPath<Material>(path);
            if (mat == null) continue;

            bool needsFix = false;
            string fixDetails = "";

            // 检查Enable GPU Instancing
            if (!mat.enableInstancing)
            {
                needsFix = true;
                fixDetails += "未启用Enable GPU Instancing; ";
            }

            // 检查Double Sided GI
            bool doubleSidedGI = false;
            try
            {
                // 反射获取材质的doubleSidedGI属性
                var so = new SerializedObject(mat);
                var prop = so.FindProperty("m_DoubleSidedGI");
                if (prop != null)
                {
                    doubleSidedGI = prop.boolValue;
                }
            }
            catch (Exception ex)
            {
                Debug.LogWarning($"检查材质Double Sided GI时出错: {path}, {ex.Message}");
            }

            if (!doubleSidedGI)
            {
                needsFix = true;
                fixDetails += "未启用Double Sided Global Illumination; ";
            }

            if (needsFix)
            {
                results.Add(new CheckResult
                {
                    name = $"材质优化建议: {Path.GetFileName(path)}",
                    description = $"此材质可进行优化。{fixDetails.Trim()}",
                    passed = false,
                    canAutoFix = true,
                    details = "",
                    fixAction = () =>
                    {
                        try
                        {
                            bool changed = false;
                            if (!mat.enableInstancing)
                            {
                                mat.enableInstancing = true;
                                changed = true;
                            }
                            // 设置Double Sided GI
                            var so = new SerializedObject(mat);
                            var prop = so.FindProperty("m_DoubleSidedGI");
                            if (prop != null && !prop.boolValue)
                            {
                                prop.boolValue = true;
                                so.ApplyModifiedProperties();
                                changed = true;
                            }
                            if (changed)
                            {
                                EditorUtility.SetDirty(mat);
                                AssetDatabase.SaveAssets();
                                Debug.Log($"已成功优化材质: {path}");
                            }
                        }
                        catch (Exception ex)
                        {
                            Debug.LogError($"优化材质 '{path}' 时发生错误: {ex.Message}\n{ex.StackTrace}");
                        }
                    }
                });
            }
        }

        checkResults["Material"] = results;
    }

    private void CheckScripts()
    {
        var results = new List<CheckResult>();
        var scriptGuids = AssetDatabase.FindAssets("t:MonoScript");

        foreach (var guid in scriptGuids)
        {
            var path = AssetDatabase.GUIDToAssetPath(guid);
            var script = AssetDatabase.LoadAssetAtPath<MonoScript>(path);
            if (script == null) continue;

            var scriptText = script.text;

            if (scriptText.Contains("void Update()") && scriptText.Contains("Update()\n    {\n    }"))
            {
                results.Add(new CheckResult
                {
                    name = $"空Update方法: {Path.GetFileName(path)}",
                    description = "MonoBehavior脚本不应具有空的Update方法",
                    passed = false,
                    canAutoFix = false,
                    details = "请删除空的Update方法以提高性能"
                });
            }

            if (scriptText.Contains("OnGUI"))
            {
                results.Add(new CheckResult
                {
                    name = $"OnGUI方法: {Path.GetFileName(path)}",
                    description = "由于内存使用率高，不应使用OnGUI方法",
                    passed = false,
                    canAutoFix = false,
                    details = "建议使用uGUI系统替代OnGUI"
                });
            }
        }

        checkResults["Script"] = results;
    }

    private static void GetTextureOriginalSize(TextureImporter ti, out int width, out int height)
    {
        if (ti == null)
        {
            width = 0;
            height = 0;
            return;
        }
        object[] args = new object[2] { 0, 0 };
        MethodInfo mi = typeof(TextureImporter).GetMethod("GetWidthAndHeight", BindingFlags.NonPublic | BindingFlags.Instance);
        mi.Invoke(ti, args);
        width = (int)args[0];
        height = (int)args[1];
    }

    private static void SetTexturePlatformSettings(TextureImporter importer, string platformName, int size, bool isPNG)
    {
        TextureImporterFormat format;
        AndroidETC2FallbackOverride androidOverride = AndroidETC2FallbackOverride.Quality16Bit;

        switch (platformName)
        {
            case "Android":
                format = isPNG ? TextureImporterFormat.ASTC_4x4 : TextureImporterFormat.DXT1;
                break;
            case "iOS":
                format = isPNG ? TextureImporterFormat.ASTC_4x4 : TextureImporterFormat.PVRTC_RGB4;
                break;
            case "Standalone":
                format = isPNG ? TextureImporterFormat.DXT5 : TextureImporterFormat.DXT1;
                break;
            default:
                format = TextureImporterFormat.Automatic;
                Debug.LogWarning($"不支持的平台 '{platformName}' 的纹理设置。对 '{importer.assetPath}' 使用自动格式。");
                break;
        }

        var platformSettings = new TextureImporterPlatformSettings
        {
            name = platformName,
            overridden = true,
            resizeAlgorithm = TextureResizeAlgorithm.Bilinear,
            format = format,
            compressionQuality = 75,
            maxTextureSize = size,
        };

        if (platformName == "Android")
        {
            platformSettings.androidETC2FallbackOverride = androidOverride;
        }

        importer.SetPlatformTextureSettings(platformSettings);
    }

    private static int GetValidTextureSize(int size)
    {
        int result = 0;
        if (size > 0 && size <= 32) result = 32;
        else if (size > 32 && size <= 64) result = 64;
        else if (size > 64 && size <= 128) result = 128;
        else if (size > 128 && size <= 256) result = 256;
        else if (size > 256 && size <= 512) result = 512;
        else if (size > 512 && size <= 1024) result = 1024;
        else if (size > 1024 && size <= 2048) result = 1024;
        else result = 1024;
        return result;
    }

    private bool IsPowerOfTwo(int value)
    {
        return (value & (value - 1)) == 0 && value > 0;
    }
}

[System.Serializable]
public class CheckResult
{
    public string name;
    public string description;
    public string details;
    public bool passed;
    public bool canAutoFix;
    public System.Action fixAction;
}
