namespace System.Runtime.Versioning;

[AttributeUsage(AttributeTargets.Assembly | AttributeTargets.Module | AttributeTargets.Class | AttributeTargets.Struct | AttributeTargets.Enum | AttributeTargets.Constructor | AttributeTargets.Method | AttributeTargets.Property | AttributeTargets.Field | AttributeTargets.Event | AttributeTargets.Interface, AllowMultiple = true, Inherited = false)]
internal sealed class UnsupportedOSPlatformAttribute : OSPlatformAttribute
{
	public string Message { get; }

	public UnsupportedOSPlatformAttribute(string platformName)
		: base(platformName)
	{
	}

	public UnsupportedOSPlatformAttribute(string platformName, string message)
		: base(platformName)
	{
		Message = message;
	}
}
