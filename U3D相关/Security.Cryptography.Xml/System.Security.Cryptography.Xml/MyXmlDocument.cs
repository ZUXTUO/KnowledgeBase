using System.Xml;

namespace System.Security.Cryptography.Xml;

internal sealed class MyXmlDocument : XmlDocument
{
	protected override XmlAttribute CreateDefaultAttribute(string prefix, string localName, string namespaceURI)
	{
		return CreateAttribute(prefix, localName, namespaceURI);
	}
}
