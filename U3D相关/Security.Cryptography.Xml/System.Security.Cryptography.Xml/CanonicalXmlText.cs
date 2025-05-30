using System.Text;
using System.Xml;

namespace System.Security.Cryptography.Xml;

internal sealed class CanonicalXmlText : XmlText, ICanonicalizableNode
{
	private bool _isInNodeSet;

	public bool IsInNodeSet
	{
		get
		{
			return _isInNodeSet;
		}
		set
		{
			_isInNodeSet = value;
		}
	}

	public CanonicalXmlText(string strData, XmlDocument doc, bool defaultNodeSetInclusionState)
		: base(strData, doc)
	{
		_isInNodeSet = defaultNodeSetInclusionState;
	}

	public void Write(StringBuilder strBuilder, DocPosition docPos, AncestralNamespaceContextManager anc)
	{
		if (IsInNodeSet)
		{
			strBuilder.Append(Utils.EscapeTextData(Value));
		}
	}

	public void WriteHash(HashAlgorithm hash, DocPosition docPos, AncestralNamespaceContextManager anc)
	{
		if (IsInNodeSet)
		{
			UTF8Encoding uTF8Encoding = new UTF8Encoding(encoderShouldEmitUTF8Identifier: false);
			byte[] bytes = uTF8Encoding.GetBytes(Utils.EscapeTextData(Value));
			hash.TransformBlock(bytes, 0, bytes.Length, bytes, 0);
		}
	}
}
