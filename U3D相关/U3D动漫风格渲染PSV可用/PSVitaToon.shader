Shader "Custom/PSVitaToonWithOutline"
{
    Properties
    {
        _Color ("Main Color", Color) = (1,1,1,1)
        _MainTex ("Base (RGB)", 2D) = "white" {}
        _ShadeTex ("Shade Ramp", 2D) = "gray" {}
        _OutlineColor ("Outline Color", Color) = (0,0,0,1)
        _OutlineWidth ("Outline Width", Float) = 0.05
    }
    SubShader
    {
        Tags { "RenderType"="Opaque" }
        
        // Outline pass
        Pass
        {
            Name "OUTLINE"
            Tags { "LightMode" = "Always" }

            // Use front-face culling for the outline pass
            Cull Front
            ZWrite On
            ZTest Less
            Offset 5,5

            CGPROGRAM
            #pragma vertex vert_outline
            #pragma fragment frag_outline
            #include "UnityCG.cginc"

            struct appdata_t
            {
                float4 vertex : POSITION;
                float3 normal : NORMAL;
                float4 texcoord : TEXCOORD0;
            };

            struct v2f
            {
                float4 pos : SV_POSITION;
            };

            uniform float _OutlineWidth;
            uniform float4 _OutlineColor;

            v2f vert_outline(appdata_t v)
            {
                v2f o;
                float3 offset = normalize(v.normal) * _OutlineWidth;
                o.pos = UnityObjectToClipPos(v.vertex + float4(offset, 0.0));
                return o;
            }

            half4 frag_outline(v2f i) : SV_Target
            {
                return _OutlineColor;
            }

            ENDCG
        }

        // Main shader pass
        Pass
        {
            Tags { "LightMode" = "ForwardBase" }
            CGPROGRAM
            #pragma vertex vert
            #pragma fragment frag
            #include "UnityCG.cginc"

            struct appdata_t
            {
                float4 vertex : POSITION;
                float3 normal : NORMAL;
                float4 texcoord : TEXCOORD0;
            };

            struct v2f
            {
                float4 pos : SV_POSITION;
                float2 uv : TEXCOORD0;
                float3 normal : TEXCOORD1;
                float3 lightDir : TEXCOORD2;
                float3 worldPos : TEXCOORD3;
            };

            sampler2D _MainTex;
            sampler2D _ShadeTex;
            fixed4 _Color;

            v2f vert(appdata_t v)
            {
                v2f o;
                o.pos = UnityObjectToClipPos(v.vertex);
                o.uv = v.texcoord.xy;
                o.normal = normalize(mul((float3x3) unity_ObjectToWorld, v.normal));
                o.lightDir = normalize(_WorldSpaceLightPos0.xyz);
                o.worldPos = mul(unity_ObjectToWorld, v.vertex).xyz;
                return o;
            }

            half4 frag(v2f i) : SV_Target
            {
                half4 texColor = tex2D(_MainTex, i.uv) * _Color;
                half NdotL = dot(i.normal, i.lightDir);
                NdotL = saturate(NdotL);
                half3 shadeColor = tex2D(_ShadeTex, float2(NdotL, 0.5)).rgb;
                half4 finalColor = half4(texColor.rgb * shadeColor, texColor.a);
                float3 lightIntensity = step(0.5, shadeColor) * 0.5 + 0.5;
                finalColor.rgb *= lightIntensity;
                return finalColor;
            }

            ENDCG
        }

        // Backface pass for outline
        Pass
        {
            Name "OUTLINE"
            Tags { "LightMode" = "Always" }

            Cull Back
            ZWrite On
            ZTest Less
            Offset 5,5

            CGPROGRAM
            #pragma vertex vert_outline
            #pragma fragment frag_outline
            #include "UnityCG.cginc"

            struct appdata_t
            {
                float4 vertex : POSITION;
                float3 normal : NORMAL;
                float4 texcoord : TEXCOORD0;
            };

            struct v2f
            {
                float4 pos : SV_POSITION;
            };

            uniform float _OutlineWidth;
            uniform float4 _OutlineColor;

            v2f vert_outline(appdata_t v)
            {
                v2f o;
                float3 offset = normalize(v.normal) * _OutlineWidth;
                o.pos = UnityObjectToClipPos(v.vertex - float4(offset, 0.0));
                return o;
            }

            half4 frag_outline(v2f i) : SV_Target
            {
                return _OutlineColor;
            }

            ENDCG
        }
    }

    Fallback "Diffuse"
}
