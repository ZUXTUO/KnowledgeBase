namespace System.Runtime.Versioning;

[AttributeUsage(AttributeTargets.Method | AttributeTargets.Property | AttributeTargets.Field, AllowMultiple = true, Inherited = false)]
internal sealed class SupportedOSPlatformGuardAttribute : OSPlatformAttribute
{
	public SupportedOSPlatformGuardAttribute(string platformName)
		: base(platformName)
	{
	}
}
