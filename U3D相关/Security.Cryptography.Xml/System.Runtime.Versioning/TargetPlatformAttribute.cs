namespace System.Runtime.Versioning;

[AttributeUsage(AttributeTargets.Assembly, AllowMultiple = false, Inherited = false)]
internal sealed class TargetPlatformAttribute : OSPlatformAttribute
{
	public TargetPlatformAttribute(string platformName)
		: base(platformName)
	{
	}
}
