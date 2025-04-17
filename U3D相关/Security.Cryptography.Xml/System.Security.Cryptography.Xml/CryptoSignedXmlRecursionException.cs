using System.Runtime.CompilerServices;
using System.Runtime.Serialization;
using System.Xml;

namespace System.Security.Cryptography.Xml;

[Serializable]
[TypeForwardedFrom("System.Security, Version=4.0.0.0, Culture=neutral, PublicKeyToken=b03f5f7f11d50a3a")]
public class CryptoSignedXmlRecursionException : XmlException
{
	public CryptoSignedXmlRecursionException()
	{
	}

	public CryptoSignedXmlRecursionException(string message)
		: base(message)
	{
	}

	public CryptoSignedXmlRecursionException(string message, Exception inner)
		: base(message, inner)
	{
	}

	protected CryptoSignedXmlRecursionException(SerializationInfo info, StreamingContext context)
		: base(info, context)
	{
	}
}
