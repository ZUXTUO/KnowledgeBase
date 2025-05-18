// ==UserScript==
// @name         极致唯美玻璃雨滴效果
// @namespace    http://tampermonkey.net/
// @version      2.0
// @description  一键添加逼真雨滴落在玻璃上的唯美朦胧效果，包含高级雨滴、动态光反射、雾气和水痕，支持夜间模式检测
// @author       ZUXTUO， Enhanced by Claude
// @match        *://*/*
// @grant        none
// ==/UserScript==

(function() {
    'use strict';

    // 创建控制按钮
    function createToggleButton() {
        const button = document.createElement('div');
        button.innerHTML = '🌧️';
        button.title = '切换唯美雨滴效果';
        button.style.cssText = `
            position: fixed;
            bottom: 20px;
            right: 20px;
            width: 50px;
            height: 50px;
            background: linear-gradient(145deg, rgba(72, 154, 209, 0.8), rgba(43, 77, 152, 0.8));
            color: white;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            font-size: 24px;
            z-index: 9999;
            box-shadow: 0 3px 15px rgba(0, 0, 0, 0.3);
            transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
            opacity: 0.9;
            backdrop-filter: blur(5px);
        `;

        button.addEventListener('mouseover', function() {
            this.style.transform = 'scale(1.1)';
            this.style.boxShadow = '0 5px 20px rgba(72, 154, 209, 0.5)';
            this.style.opacity = '1';
        });

        button.addEventListener('mouseout', function() {
            this.style.transform = 'scale(1)';
            this.style.boxShadow = '0 3px 15px rgba(0, 0, 0, 0.3)';
            this.style.opacity = '0.9';
        });

        button.addEventListener('click', toggleRainEffect);
        document.body.appendChild(button);
    }

    // 创建设置面板
    function createSettingsPanel() {
        const settingsPanel = document.createElement('div');
        settingsPanel.id = 'rain-settings-panel';
        settingsPanel.style.cssText = `
            position: fixed;
            bottom: 80px;
            right: 20px;
            width: 220px;
            background: linear-gradient(135deg, rgba(35,40,65,0.85) 0%, rgba(20,25,40,0.95) 100%);
            backdrop-filter: blur(10px);
            border-radius: 12px;
            padding: 15px;
            color: white;
            font-family: Arial, sans-serif;
            z-index: 9998;
            box-shadow: 0 5px 25px rgba(0,0,0,0.3);
            transform: translateY(20px);
            opacity: 0;
            transition: all 0.4s cubic-bezier(0.19, 1, 0.22, 1);
            display: none;
            border: 1px solid rgba(255,255,255,0.1);
        `;

        // 设置面板内容
        settingsPanel.innerHTML = `
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
                <h3 style="margin: 0; font-size: 16px; font-weight: 500;">雨滴效果设置</h3>
                <div id="close-settings" style="cursor: pointer; font-size: 18px;">×</div>
            </div>

            <div style="margin-bottom: 12px;">
                <label style="display: block; margin-bottom: 5px; font-size: 13px; opacity: 0.8;">雨滴密度</label>
                <input id="rain-density" type="range" min="1" max="10" value="5" style="width: 100%; accent-color: #4899d1;">
            </div>

            <div style="margin-bottom: 12px;">
                <label style="display: block; margin-bottom: 5px; font-size: 13px; opacity: 0.8;">雨滴大小</label>
                <input id="rain-size" type="range" min="1" max="10" value="5" style="width: 100%; accent-color: #4899d1;">
            </div>

            <div style="margin-bottom: 12px;">
                <label style="display: block; margin-bottom: 5px; font-size: 13px; opacity: 0.8;">模糊程度</label>
                <input id="blur-level" type="range" min="0" max="10" value="2" style="width: 100%; accent-color: #4899d1;">
            </div>

            <div style="margin-bottom: 12px; display: flex; align-items: center;">
                <input id="use-dark-mode" type="checkbox" checked style="margin-right: 8px;">
                <label style="font-size: 13px; opacity: 0.8;">启用朦胧玻璃效果</label>
            </div>

            <div style="text-align: center; margin-top: 10px;">
                <button id="apply-settings" style="background: linear-gradient(135deg, #4899d1, #2b4d98); border: none; color: white; padding: 6px 16px; border-radius: 5px; cursor: pointer; font-size: 13px;">应用设置</button>
            </div>
        `;

        document.body.appendChild(settingsPanel);

        // 关闭设置面板
        document.getElementById('close-settings').addEventListener('click', () => {
            settingsPanel.style.opacity = '0';
            settingsPanel.style.transform = 'translateY(20px)';
            setTimeout(() => {
                settingsPanel.style.display = 'none';
            }, 400);
        });

        // 应用设置
        document.getElementById('apply-settings').addEventListener('click', () => {
            rainSettings.density = parseInt(document.getElementById('rain-density').value);
            rainSettings.size = parseInt(document.getElementById('rain-size').value);
            rainSettings.blurLevel = parseInt(document.getElementById('blur-level').value);
            rainSettings.useDarkMode = document.getElementById('use-dark-mode').checked;

            // 如果当前已启用，则重新应用效果
            if (isEnabled) {
                removeRainEffect();
                applyEffects();
            }

            // 关闭面板
            settingsPanel.style.opacity = '0';
            settingsPanel.style.transform = 'translateY(20px)';
            setTimeout(() => {
                settingsPanel.style.display = 'none';
            }, 400);
        });

        return settingsPanel;
    }

    // 显示设置面板
    function showSettingsPanel() {
        const settingsPanel = document.getElementById('rain-settings-panel') || createSettingsPanel();
        settingsPanel.style.display = 'block';

        // 更新面板显示当前设置
        document.getElementById('rain-density').value = rainSettings.density;
        document.getElementById('rain-size').value = rainSettings.size;
        document.getElementById('blur-level').value = rainSettings.blurLevel;
        document.getElementById('use-dark-mode').checked = rainSettings.useDarkMode;

        setTimeout(() => {
            settingsPanel.style.opacity = '1';
            settingsPanel.style.transform = 'translateY(0)';
        }, 10);
    }

    // 创建设置图标
    function createSettingsButton() {
        const settingsBtn = document.createElement('div');
        settingsBtn.innerHTML = '⚙️';
        settingsBtn.title = '雨滴效果设置';
        settingsBtn.style.cssText = `
            position: fixed;
            bottom: 20px;
            right: 80px;
            width: 40px;
            height: 40px;
            background: linear-gradient(145deg, rgba(100, 100, 120, 0.6), rgba(60, 60, 80, 0.6));
            color: white;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            font-size: 18px;
            z-index: 9999;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.25);
            transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
            opacity: 0.85;
            backdrop-filter: blur(5px);
        `;

        settingsBtn.addEventListener('mouseover', function() {
            this.style.transform = 'scale(1.1)';
            this.style.opacity = '1';
        });

        settingsBtn.addEventListener('mouseout', function() {
            this.style.transform = 'scale(1)';
            this.style.opacity = '0.85';
        });

        settingsBtn.addEventListener('click', showSettingsPanel);
        document.body.appendChild(settingsBtn);
    }

    // 存储原始样式以便恢复
    let originalStyles = {};
    let isEnabled = false;
    let rainContainer = null;
    let darkModeStyleElement = null;
    let lightEffectsContainer = null;

    // 雨滴效果设置
    let rainSettings = {
        density: 5,
        size: 5,
        blurLevel: 2,
        useDarkMode: true
    };

    // 检测网页是否有自带夜间模式
    function detectNightMode() {
        // 方法1: 检查meta标签
        const metaTags = document.querySelectorAll('meta[name*="theme-color"], meta[name*="color-scheme"]');
        for (const tag of metaTags) {
            if (tag.content && tag.content.toLowerCase().includes('dark')) {
                return true;
            }
        }

        // 方法2: 检查常见的夜间模式CSS类名
        const bodyClasses = document.body.className.toLowerCase();
        const htmlClasses = document.documentElement.className.toLowerCase();
        const darkClasses = ['dark', 'dark-mode', 'night', 'night-mode', 'darkmode', 'dark-theme', 'darktheme'];

        for (const cls of darkClasses) {
            if (bodyClasses.includes(cls) || htmlClasses.includes(cls)) {
                return true;
            }
        }

        // 方法3: 检查媒体查询偏好
        if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
            return true;
        }

        // 方法4: 检查背景颜色是否为深色
        const bodyBgColor = window.getComputedStyle(document.body).backgroundColor;
        const htmlBgColor = window.getComputedStyle(document.documentElement).backgroundColor;

        function isColorDark(color) {
            // 提取RGB值
            const rgba = color.match(/\d+/g);
            if (!rgba || rgba.length < 3) return false;

            // 计算亮度 (以RGB值的加权平均来估算)
            const brightness = (parseInt(rgba[0]) * 0.299 + parseInt(rgba[1]) * 0.587 + parseInt(rgba[2]) * 0.114) / 255;
            return brightness < 0.5; // 亮度小于0.5认为是深色
        }

        if (isColorDark(bodyBgColor) || isColorDark(htmlBgColor)) {
            return true;
        }

        return false;
    }

    // 切换雨滴效果
    function toggleRainEffect() {
        if (isEnabled) {
            removeRainEffect();
            removeDarkMode();
            isEnabled = false;
        } else {
            applyEffects();
            isEnabled = true;
        }
    }

    // 应用所有效果
    function applyEffects() {
        // 检测网页是否已有夜间模式
        const hasNightMode = detectNightMode();

        // 如果网页没有夜间模式并且用户选择了使用朦胧效果，则应用我们的效果
        if (!hasNightMode && rainSettings.useDarkMode) {
            applyDarkMode();
        }

        createRainEffect();
        createLightEffects();
    }

    // 应用暗黑模式（只添加玻璃雾气效果，不添加背景色）
    function applyDarkMode() {
        // 备份原始样式
        saveOriginalStyles();

        darkModeStyleElement = document.createElement('style');
        darkModeStyleElement.id = 'dark-mode-style';
        darkModeStyleElement.innerHTML = `
            html:before {
                content: "";
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: linear-gradient(135deg, rgba(255,255,255,0.05) 0%, rgba(255,255,255,0.08) 100%);
                backdrop-filter: blur(${rainSettings.blurLevel * 0.25}px);
                pointer-events: none;
                z-index: 999;
            }
        `;
        document.head.appendChild(darkModeStyleElement);
    }

    // 保存原始样式以便恢复
    function saveOriginalStyles() {
        originalStyles.bodyBackground = document.body.style.backgroundColor;
        originalStyles.bodyColor = document.body.style.color;
    }

    // 移除暗黑模式
    function removeDarkMode() {
        if (darkModeStyleElement) {
            darkModeStyleElement.remove();
        }
    }

    // 创建雨滴效果
    function createRainEffect() {
        // 创建雨滴容器
        rainContainer = document.createElement('div');
        rainContainer.id = 'rain-container';
        rainContainer.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            pointer-events: none;
            z-index: 9998;
            overflow: hidden;
        `;
        document.body.appendChild(rainContainer);

        // 添加雨滴玻璃效果CSS
        const rainStyle = document.createElement('style');
        rainStyle.id = 'rain-style';
        rainStyle.innerHTML = `
            .raindrop {
                position: absolute;
                background: linear-gradient(170deg,
                    rgba(255,255,255,0.25) 0%,
                    rgba(255,255,255,0.15) 40%,
                    rgba(255,255,255,0.35) 40.5%,
                    rgba(255,255,255,0.4) 100%);
                border-radius: 50% 50% 48% 48% / 60% 60% 40% 40%;
                box-shadow:
                    inset 0 0 3px rgba(255,255,255,0.5),
                    inset 5px 3px 10px rgba(255,255,255,0.15),
                    0 0 5px rgba(255,255,255,0.4);
                pointer-events: none;
                transform-origin: center bottom;
                z-index: 9997;
                backface-visibility: hidden;
            }

            .raindrop:before {
                content: '';
                position: absolute;
                top: 5%;
                left: 15%;
                width: 35%;
                height: 30%;
                background: radial-gradient(ellipse at center, rgba(255,255,255,0.6) 0%, rgba(255,255,255,0) 80%);
                border-radius: 50%;
                z-index: 2;
            }

            .rain-trail {
                position: absolute;
                background: linear-gradient(to bottom,
                    rgba(255,255,255,0.07) 0%,
                    rgba(255,255,255,0.15) 50%,
                    rgba(255,255,255,0.07) 100%);
                pointer-events: none;
                border-radius: 50% 50% 25% 25% / 60% 60% 40% 40%;
                z-index: 9996;
                backdrop-filter: blur(1px);
            }

            .splash {
                position: absolute;
                background: radial-gradient(circle,
                    rgba(255,255,255,0.5) 0%,
                    rgba(255,255,255,0.2) 50%,
                    rgba(255,255,255,0) 100%);
                border-radius: 50%;
                transform-origin: center center;
                animation: splash 1s cubic-bezier(0.165, 0.84, 0.44, 1) forwards;
                z-index: 9997;
            }

            .splash:before {
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background: radial-gradient(circle at 30% 30%,
                    rgba(255,255,255,0.4) 0%,
                    rgba(255,255,255,0) 80%);
                border-radius: 50%;
            }

            .micro-splash {
                position: absolute;
                background: radial-gradient(circle,
                    rgba(255,255,255,0.4) 0%,
                    rgba(255,255,255,0.1) 70%,
                    rgba(255,255,255,0) 100%);
                border-radius: 50%;
                transform-origin: center center;
                animation: microSplash 0.5s ease-out forwards;
                z-index: 9996;
            }

            .fog-patch {
                position: absolute;
                background: radial-gradient(ellipse,
                    rgba(255,255,255,0.15) 0%,
                    rgba(255,255,255,0.05) 60%,
                    rgba(255,255,255,0) 100%);
                border-radius: 50%;
                pointer-events: none;
                opacity: 0;
                animation: fogFade 15s ease-in-out infinite alternate;
                z-index: 9995;
                mix-blend-mode: overlay;
            }

            .water-streak {
                position: absolute;
                background: linear-gradient(to bottom,
                    rgba(255,255,255,0.01) 0%,
                    rgba(255,255,255,0.07) 50%,
                    rgba(255,255,255,0.01) 100%);
                border-radius: 0 0 40% 40%;
                pointer-events: none;
                z-index: 9994;
                opacity: 0.7;
                backdrop-filter: blur(0.5px);
            }

            .light-reflection {
                position: absolute;
                background: radial-gradient(ellipse at center,
                    rgba(255,255,255,0.7) 0%,
                    rgba(255,255,255,0.3) 30%,
                    rgba(255,255,255,0) 70%);
                border-radius: 50%;
                mix-blend-mode: screen;
                opacity: 0;
                animation: reflectionFade 3s ease-in-out infinite;
                pointer-events: none;
                z-index: 9994;
            }

            @keyframes splash {
                0% {
                    transform: scale(0);
                    opacity: 0.9;
                }
                100% {
                    transform: scale(1);
                    opacity: 0;
                }
            }

            @keyframes microSplash {
                0% {
                    transform: scale(0);
                    opacity: 0.8;
                }
                100% {
                    transform: scale(1);
                    opacity: 0;
                }
            }

            @keyframes fogFade {
                0% {
                    opacity: 0.05;
                    transform: scale(1);
                }
                50% {
                    opacity: 0.15;
                    transform: scale(1.03);
                }
                100% {
                    opacity: 0.1;
                    transform: scale(1);
                }
            }

            @keyframes reflectionFade {
                0%, 100% {
                    opacity: 0;
                }
                50% {
                    opacity: 0.3;
                }
            }
        `;
        document.head.appendChild(rainStyle);

        // 开始创建雨滴
        createRaindrops();

        // 创建水痕
        createWaterStreaks();
    }

    // 创建光效容器
    function createLightEffects() {
        // 创建光效容器
        lightEffectsContainer = document.createElement('div');
        lightEffectsContainer.id = 'light-effects-container';
        lightEffectsContainer.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            pointer-events: none;
            z-index: 9993;
            overflow: hidden;
        `;
        document.body.appendChild(lightEffectsContainer);

        // 添加初始光反射点
        for (let i = 0; i < 5; i++) {
            createLightReflection();
        }

        // 每隔一段时间创建新的光反射
        setInterval(() => {
            if (lightEffectsContainer && document.body.contains(lightEffectsContainer)) {
                createLightReflection();
            }
        }, 2000);
    }

    // 创建雨滴
    function createRaindrops() {
        // 基于密度调整雨滴生成频率
        const interval = Math.max(10, 100 - (rainSettings.density * 10));

        const rainAnimation = setInterval(() => {
            if (!rainContainer || !document.body.contains(rainContainer)) {
                clearInterval(rainAnimation);
                return;
            }

            const raindrop = document.createElement('div');
            raindrop.className = 'raindrop';

            // 基于大小设置调整雨滴大小
            const sizeMultiplier = rainSettings.size / 5;
            const size = (Math.random() * 8 + 3) * sizeMultiplier;
            const posX = Math.random() * window.innerWidth;
            const posY = -20;

            // 速度与大小成正比，但有随机变化
            const velocity = (Math.random() * 2 + 1) * (0.5 + size / 10);
            const duration = Math.random() * 1.8 + 1;

            // 更自然的雨滴形状（稍微拉长）
            const height = size * (1.5 + Math.random() * 0.5);

            raindrop.style.cssText = `
                width: ${size}px;
                height: ${height}px;
                left: ${posX}px;
                top: ${posY}px;
                opacity: ${Math.random() * 0.7 + 0.3};
                transform: rotate(${Math.random() * 10 - 5}deg);
                filter: blur(${Math.random() * 0.5}px);
            `;

            rainContainer.appendChild(raindrop);

            // 为大雨滴添加内部高光效果
            if (size > 6) {
                const highlight = document.createElement('div');
                highlight.style.cssText = `
                    position: absolute;
                    top: ${Math.random() * 40}%;
                    left: ${Math.random() * 30 + 10}%;
                    width: ${size * 0.4}px;
                    height: ${size * 0.2}px;
                    background: radial-gradient(ellipse at center, rgba(255,255,255,0.8) 0%, rgba(255,255,255,0) 80%);
                    border-radius: 50%;
                    transform: rotate(${Math.random() * 30 - 15}deg);
                    opacity: ${Math.random() * 0.3 + 0.4};
                `;
                raindrop.appendChild(highlight);
            }

            // 雨滴落下动画
            let positionY = posY;
            const fallAnimation = setInterval(() => {
                if (!rainContainer || !document.body.contains(rainContainer) || !document.body.contains(raindrop)) {
                    clearInterval(fallAnimation);
                    return;
                }

                positionY += velocity;
                raindrop.style.top = `${positionY}px`;

                // 随机左右微移（模拟自然下落）
                if (Math.random() > 0.8) {
                    const currLeft = parseFloat(raindrop.style.left);
                    const wiggle = Math.random() * 2 - 1;
                    raindrop.style.left = `${currLeft + wiggle}px`;

                    // 微量旋转以增加自然感
                    const currRotation = parseFloat(raindrop.style.transform.replace(/[^\d.-]/g, '')) || 0;
                    raindrop.style.transform = `rotate(${currRotation + wiggle * 0.2}deg)`;
                }

                // 雨滴落到底部时
                if (positionY > window.innerHeight) {
                    clearInterval(fallAnimation);

                    // 创建随机数量的微小溅落
                    const splashCount = Math.floor(Math.random() * 3) + 1;
                    for (let i = 0; i < splashCount; i++) {
                        createMicroSplash(posX + (Math.random() * 10 - 5), window.innerHeight - (Math.random() * 3));
                    }

                    // 创建主溅落效果
                    createSplash(posX, window.innerHeight);

                    raindrop.remove();
                }
            }, 16);

            // 随机添加拖尾效果
            if (Math.random() > 0.5) {
                createRainTrail(posX, posY, size, duration);
            }
        }, interval);

        // 添加随机雾气斑块
        createFogPatches();
    }

    // 创建雨滴拖尾
    function createRainTrail(x, y, size, duration) {
        const trail = document.createElement('div');
        trail.className = 'rain-trail';

        const trailWidth = size * 0.7;
        const trailHeight = Math.random() * 100 + 50;

        trail.style.cssText = `
            width: ${trailWidth}px;
            height: ${trailHeight}px;
            left: ${x + size/2 - trailWidth/2}px;
            top: ${y}px;
            opacity: ${Math.random() * 0.25 + 0.1};
            transform: rotate(${Math.random() * 6 - 3}deg);
            filter: blur(${Math.random() * 0.5 + 0.1}px);
        `;

        rainContainer.appendChild(trail);

        // 拖尾落下和消失动画
        setTimeout(() => {
            trail.style.transition = `top ${duration * 1.2}s cubic-bezier(0.25, 0.46, 0.45, 0.94), opacity ${duration}s ease-out`;
            trail.style.top = `${window.innerHeight}px`;
            trail.style.opacity = '0';

            setTimeout(() => {
                if (trail && document.body.contains(trail)) {
                    trail.remove();
                }
            }, duration * 1200);
        }, 10);
    }

    // 创建溅落效果
    function createSplash(x, y) {
        const splash = document.createElement('div');
        splash.className = 'splash';

        const size = Math.random() * 20 + 10;

        splash.style.cssText = `
            width: ${size}px;
            height: ${size}px;
            left: ${x - size/2}px;
            top: ${y - size/2}px;
            transform: scale(0);
        `;

        rainContainer.appendChild(splash);

        // 溅落后自动移除
        setTimeout(() => {
            if (splash && document.body.contains(splash)) {
                splash.remove();
            }
        }, 1000);
    }

    // 创建微小溅落
    function createMicroSplash(x, y) {
        const microSplash = document.createElement('div');
        microSplash.className = 'micro-splash';

        const size = Math.random() * 8 + 3;

        microSplash.style.cssText = `
            width: ${size}px;
            height: ${size}px;
            left: ${x - size/2}px;
            top: ${y - size/2}px;
            transform: scale(0);
        `;

        rainContainer.appendChild(microSplash);

        // 微小溅落后自动移除
        setTimeout(() => {
            if (microSplash && document.body.contains(microSplash)) {
                microSplash.remove();
            }
        }, 500);
    }

    // 创建雾气斑块效果
    function createFogPatches() {
        // 根据设置调整雾气斑块数量
        const fogPatchCount = Math.max(5, Math.floor(10 * rainSettings.density / 5));

        // 创建初始雾气
        for (let i = 0; i < fogPatchCount; i++) {
            createFogPatch();
        }

        // 每隔一段时间创建新的雾气斑块
        setInterval(() => {
            if (rainContainer && document.body.contains(rainContainer)) {
                if (Math.random() > 0.6) {
                    createFogPatch();
                }
            }
        }, 3000);
    }

    // 创建单个雾气斑块
    function createFogPatch() {
        const fog = document.createElement('div');
        fog.className = 'fog-patch';

        const size = Math.random() * 250 + 100;
        const posX = Math.random() * window.innerWidth;
        const posY = Math.random() * window.innerHeight;
        const opacity = Math.random() * 0.12 + 0.05;
        const blurAmount = Math.random() * 5 + 2;

        fog.style.cssText = `
            width: ${size}px;
            height: ${size * (Math.random() * 0.5 + 0.75)}px;
            left: ${posX - size/2}px;
            top: ${posY - size/2}px;
            opacity: ${opacity};
            filter: blur(${blurAmount}px);
            animation-duration: ${Math.random() * 10 + 10}s;
            animation-delay: ${Math.random() * 5}s;
            transform: rotate(${Math.random() * 360}deg);
        `;

        rainContainer.appendChild(fog);

        // 雾气自动淡出
        setTimeout(() => {
            if (fog && document.body.contains(fog)) {
                fog.style.transition = 'opacity 5s ease-out, transform 8s ease-in-out';
                fog.style.opacity = '0';
                fog.style.transform = `rotate(${Math.random() * 360}deg) scale(${Math.random() * 0.3 + 1.1})`;

                setTimeout(() => {
                    if (fog && document.body.contains(fog)) {
                        fog.remove();
                    }
                }, 5000);
            }
        }, Math.random() * 20000 + 15000);
    }

    // 创建水痕效果
    function createWaterStreaks() {
        // 根据设置调整水痕数量
        const streakCount = Math.max(3, Math.floor(10 * rainSettings.size / 5));

        // 创建初始水痕
        for (let i = 0; i < streakCount; i++) {
            createWaterStreak();
        }

        // 每隔一段时间创建新的水痕
        setInterval(() => {
            if (rainContainer && document.body.contains(rainContainer)) {
                if (Math.random() > 0.7) {
                    createWaterStreak();
                }
            }
        }, 5000);
    }

    // 创建单个水痕
    function createWaterStreak() {
        const streak = document.createElement('div');
        streak.className = 'water-streak';

        const width = Math.random() * 3 + 1;
        const height = Math.random() * 300 + 100;
        const posX = Math.random() * window.innerWidth;
        const posY = Math.random() * (window.innerHeight - height);
        const opacity = Math.random() * 0.5 + 0.3;

        streak.style.cssText = `
            width: ${width}px;
            height: ${height}px;
            left: ${posX}px;
            top: ${posY}px;
            opacity: ${opacity};
            transform: rotate(${Math.random() * 2 - 1}deg);
            filter: blur(${Math.random() * 0.3 + 0.1}px);
        `;

        rainContainer.appendChild(streak);

        // 水痕移动和消失动画
        let moved = false;

        // 随机决定是否让水痕流动
        if (Math.random() > 0.5) {
            setTimeout(() => {
                if (streak && document.body.contains(streak)) {
                    streak.style.transition = `top ${Math.random() * 10 + 20}s linear, opacity ${Math.random() * 5 + 10}s ease-in-out`;
                    streak.style.top = `${parseFloat(streak.style.top) + Math.random() * 100 + 50}px`;
                    moved = true;
                }
            }, Math.random() * 2000);
        }

        // 水痕自动淡出
        setTimeout(() => {
            if (streak && document.body.contains(streak)) {
                streak.style.transition = `opacity ${Math.random() * 3 + 5}s ease-out${moved ? '' : ', top 10s ease-in'}`;
                streak.style.opacity = '0';

                if (!moved && Math.random() > 0.5) {
                    streak.style.top = `${parseFloat(streak.style.top) + Math.random() * 50 + 20}px`;
                }

                setTimeout(() => {
                    if (streak && document.body.contains(streak)) {
                        streak.remove();
                    }
                }, 8000);
            }
        }, Math.random() * 15000 + 10000);
    }

    // 创建光反射效果
    function createLightReflection() {
        if (!lightEffectsContainer || !document.body.contains(lightEffectsContainer)) {
            return;
        }

        const reflection = document.createElement('div');
        reflection.className = 'light-reflection';

        const size = Math.random() * 150 + 50;
        const posX = Math.random() * window.innerWidth;
        const posY = Math.random() * window.innerHeight;

        reflection.style.cssText = `
            width: ${size}px;
            height: ${size * (Math.random() * 0.3 + 0.7)}px;
            left: ${posX - size/2}px;
            top: ${posY - size/2}px;
            animation-duration: ${Math.random() * 5 + 5}s;
            animation-delay: ${Math.random() * 2}s;
            transform: rotate(${Math.random() * 360}deg);
            filter: blur(${Math.random() * 2 + 1}px);
        `;

        lightEffectsContainer.appendChild(reflection);

        // 光反射自动移除
        setTimeout(() => {
            if (reflection && document.body.contains(reflection)) {
                reflection.remove();
            }
        }, 10000);
    }

    // 移除雨滴效果
    function removeRainEffect() {
        if (rainContainer) {
            rainContainer.remove();
        }

        if (lightEffectsContainer) {
            lightEffectsContainer.remove();
        }

        const rainStyle = document.getElementById('rain-style');
        if (rainStyle) {
            rainStyle.remove();
        }
    }

    // 性能优化：检测页面是否可见，在不可见时暂停动画
    document.addEventListener('visibilitychange', function() {
        if (document.hidden) {
            // 页面不可见时暂停所有动画
            if (rainContainer) {
                rainContainer.style.animationPlayState = 'paused';
                const elements = rainContainer.querySelectorAll('*');
                elements.forEach(el => {
                    el.style.animationPlayState = 'paused';
                    el.style.transitionProperty = 'none';
                });
            }

            if (lightEffectsContainer) {
                lightEffectsContainer.style.animationPlayState = 'paused';
                const elements = lightEffectsContainer.querySelectorAll('*');
                elements.forEach(el => {
                    el.style.animationPlayState = 'paused';
                    el.style.transitionProperty = 'none';
                });
            }
        } else {
            // 页面可见时恢复所有动画
            if (rainContainer) {
                rainContainer.style.animationPlayState = 'running';
                const elements = rainContainer.querySelectorAll('*');
                elements.forEach(el => {
                    el.style.animationPlayState = 'running';
                    el.style.transitionProperty = '';
                });
            }

            if (lightEffectsContainer) {
                lightEffectsContainer.style.animationPlayState = 'running';
                const elements = lightEffectsContainer.querySelectorAll('*');
                elements.forEach(el => {
                    el.style.animationPlayState = 'running';
                    el.style.transitionProperty = '';
                });
            }
        }
    });

    // 窗口大小调整时重新创建雨滴效果
    let resizeTimeout;
    window.addEventListener('resize', function() {
        clearTimeout(resizeTimeout);
        resizeTimeout = setTimeout(function() {
            if (isEnabled) {
                removeRainEffect();
                applyEffects();
            }
        }, 200);
    });

    // 创建信息提示框
    function createInfoToast(message, duration = 3000) {
        const toast = document.createElement('div');
        toast.textContent = message;
        toast.style.cssText = `
            position: fixed;
            bottom: 80px;
            left: 50%;
            transform: translateX(-50%) translateY(20px);
            background: linear-gradient(135deg, rgba(35,40,65,0.85), rgba(20,25,40,0.95));
            color: white;
            padding: 8px 16px;
            border-radius: 8px;
            font-size: 14px;
            box-shadow: 0 3px 10px rgba(0,0,0,0.2);
            z-index: 10000;
            opacity: 0;
            transition: all 0.3s ease;
            backdrop-filter: blur(5px);
            border: 1px solid rgba(255,255,255,0.1);
        `;

        document.body.appendChild(toast);

        setTimeout(() => {
            toast.style.opacity = '1';
            toast.style.transform = 'translateX(-50%) translateY(0)';
        }, 10);

        setTimeout(() => {
            toast.style.opacity = '0';
            toast.style.transform = 'translateX(-50%) translateY(20px)';

            setTimeout(() => {
                if (toast && document.body.contains(toast)) {
                    toast.remove();
                }
            }, 300);
        }, duration);
    }

    // 初始化
    function initialize() {
        createToggleButton();
        createSettingsButton();

        // 检查是否有夜间模式
        const hasNightMode = detectNightMode();
        if (hasNightMode) {
            rainSettings.useDarkMode = false;
            createInfoToast('检测到网页已有夜间模式，已自动关闭朦胧玻璃效果', 5000);
        }
    }

    // 启动
    initialize();
})();