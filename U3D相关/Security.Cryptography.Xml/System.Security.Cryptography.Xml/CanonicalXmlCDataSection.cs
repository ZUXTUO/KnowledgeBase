using System.Text;
using System.Xml;

namespace System.Security.Cryptography.Xml;

internal sealed class CanonicalXmlCDataSection : XmlCDataSection, ICanonicalizableNode
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

	public CanonicalXmlCDataSection(string data, XmlDocument doc, bool defaultNodeSetInclusionState)
		: base(data, doc)
	{
		_isInNodeSet = defaultNodeSetInclusionState;
	}

	public void Write(StringBuilder strBuilder, DocPosition docPos, AncestralNamespaceContextManager anc)
	{
		if (IsInNodeSet)
		{
			strBuilder.Append(Utils.EscapeCData(Data));
		}
	}

	public void WriteHash(HashAlgorithm hash, DocPosition docPos, AncestralNamespaceContextManager anc)
	{
		if (IsInNodeSet)
		{
			UTF8Encoding uTF8Encoding = new UTF8Encoding(encoderShouldEmitUTF8Identifier: false);
			byte[] bytes = uTF8Encoding.GetBytes(Utils.EscapeCData(Data));
			hash.TransformBlock(bytes, 0, bytes.Length, bytes, 0);
		}
	}
}
