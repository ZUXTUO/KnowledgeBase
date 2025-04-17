using System.IO;
using System.Xml;

namespace System.Security.Cryptography.Xml;

public class XmlDsigC14NTransform : Transform
{
	private readonly Type[] _inputTypes = new Type[3]
	{
		typeof(Stream),
		typeof(XmlDocument),
		typeof(XmlNodeList)
	};

	private readonly Type[] _outputTypes = new Type[1] { typeof(Stream) };

	private CanonicalXml _cXml;

	private readonly bool _includeComments;

	public override Type[] InputTypes => _inputTypes;

	public override Type[] OutputTypes => _outputTypes;

	public XmlDsigC14NTransform()
	{
		base.Algorithm = "http://www.w3.org/TR/2001/REC-xml-c14n-20010315";
	}

	public XmlDsigC14NTransform(bool includeComments)
	{
		_includeComments = includeComments;
		base.Algorithm = (includeComments ? "http://www.w3.org/TR/2001/REC-xml-c14n-20010315#WithComments" : "http://www.w3.org/TR/2001/REC-xml-c14n-20010315");
	}

	public override void LoadInnerXml(XmlNodeList nodeList)
	{
		if (nodeList != null && nodeList.Count > 0)
		{
			throw new CryptographicException(System.SR.Cryptography_Xml_UnknownTransform);
		}
	}

	protected override XmlNodeList GetInnerXml()
	{
		return null;
	}

	public override void LoadInput(object obj)
	{
		XmlResolver resolver = (base.ResolverSet ? _xmlResolver : XmlResolverHelper.GetThrowingResolver());
		if (obj is Stream)
		{
			_cXml = new CanonicalXml((Stream)obj, _includeComments, resolver, base.BaseURI);
			return;
		}
		if (obj is XmlDocument)
		{
			_cXml = new CanonicalXml((XmlDocument)obj, resolver, _includeComments);
			return;
		}
		if (obj is XmlNodeList)
		{
			_cXml = new CanonicalXml((XmlNodeList)obj, resolver, _includeComments);
			return;
		}
		throw new ArgumentException(System.SR.Cryptography_Xml_IncorrectObjectType, "obj");
	}

	public override object GetOutput()
	{
		return new MemoryStream(_cXml.GetBytes());
	}

	public override object GetOutput(Type type)
	{
		if (type != typeof(Stream) && !type.IsSubclassOf(typeof(Stream)))
		{
			throw new ArgumentException(System.SR.Cryptography_Xml_TransformIncorrectInputType, "type");
		}
		return new MemoryStream(_cXml.GetBytes());
	}

	public override byte[] GetDigestedOutput(HashAlgorithm hash)
	{
		return _cXml.GetDigestedBytes(hash);
	}
}
