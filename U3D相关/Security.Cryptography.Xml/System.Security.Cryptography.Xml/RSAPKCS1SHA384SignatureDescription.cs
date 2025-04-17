namespace System.Security.Cryptography.Xml;

internal sealed class RSAPKCS1SHA384SignatureDescription : RSAPKCS1SignatureDescription
{
	public RSAPKCS1SHA384SignatureDescription()
		: base("SHA384")
	{
	}

	public sealed override HashAlgorithm CreateDigest()
	{
		return SHA384.Create();
	}
}
