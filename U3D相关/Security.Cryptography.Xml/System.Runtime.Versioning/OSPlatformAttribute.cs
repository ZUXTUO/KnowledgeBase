namespace System.Runtime.Versioning;

internal abstract class OSPlatformAttribute : Attribute
{
	public string PlatformName { get; }

	private protected OSPlatformAttribute(string platformName)
	{
		PlatformName = platformName;
	}
}
