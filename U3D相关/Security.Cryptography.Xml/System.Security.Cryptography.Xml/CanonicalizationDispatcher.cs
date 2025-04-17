using System.Text;
using System.Xml;

namespace System.Security.Cryptography.Xml;

internal static class CanonicalizationDispatcher
{
	public static void Write(XmlNode node, StringBuilder strBuilder, DocPosition docPos, AncestralNamespaceContextManager anc)
	{
		if (node is ICanonicalizableNode)
		{
			((ICanonicalizableNode)node).Write(strBuilder, docPos, anc);
		}
		else
		{
			WriteGenericNode(node, strBuilder, docPos, anc);
		}
	}

	public static void WriteGenericNode(XmlNode node, StringBuilder strBuilder, DocPosition docPos, AncestralNamespaceContextManager anc)
	{
		if (node == null)
		{
			throw new ArgumentNullException("node");
		}
		XmlNodeList childNodes = node.ChildNodes;
		foreach (XmlNode item in childNodes)
		{
			Write(item, strBuilder, docPos, anc);
		}
	}

	public static void WriteHash(XmlNode node, HashAlgorithm hash, DocPosition docPos, AncestralNamespaceContextManager anc)
	{
		if (node is ICanonicalizableNode)
		{
			((ICanonicalizableNode)node).WriteHash(hash, docPos, anc);
		}
		else
		{
			WriteHashGenericNode(node, hash, docPos, anc);
		}
	}

	public static void WriteHashGenericNode(XmlNode node, HashAlgorithm hash, DocPosition docPos, AncestralNamespaceContextManager anc)
	{
		if (node == null)
		{
			throw new ArgumentNullException("node");
		}
		XmlNodeList childNodes = node.ChildNodes;
		foreach (XmlNode item in childNodes)
		{
			WriteHash(item, hash, docPos, anc);
		}
	}
}
