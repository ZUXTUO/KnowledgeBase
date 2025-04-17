using System.IO;
using System.Xml;

namespace System.Security.Cryptography.Xml;

public class XmlLicenseTransform : Transform
{
	private readonly Type[] _inputTypes = new Type[1] { typeof(XmlDocument) };

	private readonly Type[] _outputTypes = new Type[1] { typeof(XmlDocument) };

	private XmlNamespaceManager _namespaceManager;

	private XmlDocument _license;

	private IRelDecryptor _relDecryptor;

	private const string ElementIssuer = "issuer";

	private const string NamespaceUriCore = "urn:mpeg:mpeg21:2003:01-REL-R-NS";

	public override Type[] InputTypes => _inputTypes;

	public override Type[] OutputTypes => _outputTypes;

	public IRelDecryptor Decryptor
	{
		get
		{
			return _relDecryptor;
		}
		set
		{
			_relDecryptor = value;
		}
	}

	public XmlLicenseTransform()
	{
		base.Algorithm = "urn:mpeg:mpeg21:2003:01-REL-R-NS:licenseTransform";
	}

	private void DecryptEncryptedGrants(XmlNodeList encryptedGrantList, IRelDecryptor decryptor)
	{
		int i = 0;
		for (int count = encryptedGrantList.Count; i < count; i++)
		{
			XmlElement xmlElement = encryptedGrantList[i].SelectSingleNode("//r:encryptedGrant/enc:EncryptionMethod", _namespaceManager) as XmlElement;
			XmlElement xmlElement2 = encryptedGrantList[i].SelectSingleNode("//r:encryptedGrant/dsig:KeyInfo", _namespaceManager) as XmlElement;
			XmlElement xmlElement3 = encryptedGrantList[i].SelectSingleNode("//r:encryptedGrant/enc:CipherData", _namespaceManager) as XmlElement;
			if (xmlElement == null || xmlElement2 == null || xmlElement3 == null)
			{
				continue;
			}
			EncryptionMethod encryptionMethod = new EncryptionMethod();
			KeyInfo keyInfo = new KeyInfo();
			CipherData cipherData = new CipherData();
			encryptionMethod.LoadXml(xmlElement);
			keyInfo.LoadXml(xmlElement2);
			cipherData.LoadXml(xmlElement3);
			MemoryStream memoryStream = null;
			Stream stream = null;
			StreamReader streamReader = null;
			try
			{
				memoryStream = new MemoryStream(cipherData.CipherValue);
				stream = _relDecryptor.Decrypt(encryptionMethod, keyInfo, memoryStream);
				if (stream == null || stream.Length == 0L)
				{
					throw new CryptographicException(System.SR.Cryptography_Xml_XrmlUnableToDecryptGrant);
				}
				streamReader = new StreamReader(stream);
				string innerXml = streamReader.ReadToEnd();
				encryptedGrantList[i].ParentNode.InnerXml = innerXml;
			}
			finally
			{
				memoryStream?.Close();
				stream?.Close();
				streamReader?.Close();
			}
		}
	}

	protected override XmlNodeList GetInnerXml()
	{
		return null;
	}

	public override object GetOutput()
	{
		return _license;
	}

	public override object GetOutput(Type type)
	{
		if (type != typeof(XmlDocument) && !type.IsSubclassOf(typeof(XmlDocument)))
		{
			throw new ArgumentException(System.SR.Cryptography_Xml_TransformIncorrectInputType, "type");
		}
		return GetOutput();
	}

	public override void LoadInnerXml(XmlNodeList nodeList)
	{
		if (nodeList != null && nodeList.Count > 0)
		{
			throw new CryptographicException(System.SR.Cryptography_Xml_UnknownTransform);
		}
	}

	public override void LoadInput(object obj)
	{
		if (base.Context == null)
		{
			throw new CryptographicException(System.SR.Cryptography_Xml_XrmlMissingContext);
		}
		_license = new XmlDocument();
		_license.PreserveWhitespace = true;
		_namespaceManager = new XmlNamespaceManager(_license.NameTable);
		_namespaceManager.AddNamespace("dsig", "http://www.w3.org/2000/09/xmldsig#");
		_namespaceManager.AddNamespace("enc", "http://www.w3.org/2001/04/xmlenc#");
		_namespaceManager.AddNamespace("r", "urn:mpeg:mpeg21:2003:01-REL-R-NS");
		if (!(base.Context.SelectSingleNode("ancestor-or-self::r:issuer[1]", _namespaceManager) is XmlElement xmlElement))
		{
			throw new CryptographicException(System.SR.Cryptography_Xml_XrmlMissingIssuer);
		}
		XmlNode xmlNode = xmlElement.SelectSingleNode("descendant-or-self::dsig:Signature[1]", _namespaceManager) as XmlElement;
		xmlNode?.ParentNode.RemoveChild(xmlNode);
		if (!(xmlElement.SelectSingleNode("ancestor-or-self::r:license[1]", _namespaceManager) is XmlElement xmlElement2))
		{
			throw new CryptographicException(System.SR.Cryptography_Xml_XrmlMissingLicence);
		}
		XmlNodeList xmlNodeList = xmlElement2.SelectNodes("descendant-or-self::r:license[1]/r:issuer", _namespaceManager);
		int i = 0;
		for (int count = xmlNodeList.Count; i < count; i++)
		{
			if (xmlNodeList[i] != xmlElement && xmlNodeList[i].LocalName == "issuer" && xmlNodeList[i].NamespaceURI == "urn:mpeg:mpeg21:2003:01-REL-R-NS")
			{
				xmlNodeList[i].ParentNode.RemoveChild(xmlNodeList[i]);
			}
		}
		XmlNodeList xmlNodeList2 = xmlElement2.SelectNodes("/r:license/r:grant/r:encryptedGrant", _namespaceManager);
		if (xmlNodeList2.Count > 0)
		{
			if (_relDecryptor == null)
			{
				throw new CryptographicException(System.SR.Cryptography_Xml_XrmlMissingIRelDecryptor);
			}
			DecryptEncryptedGrants(xmlNodeList2, _relDecryptor);
		}
		_license.InnerXml = xmlElement2.OuterXml;
	}
}
