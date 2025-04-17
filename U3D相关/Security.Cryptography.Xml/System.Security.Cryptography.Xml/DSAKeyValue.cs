using System.Runtime.Versioning;
using System.Xml;

namespace System.Security.Cryptography.Xml;

public class DSAKeyValue : KeyInfoClause
{
	private DSA _key;

	private const string KeyValueElementName = "KeyValue";

	private const string DSAKeyValueElementName = "DSAKeyValue";

	private const string PElementName = "P";

	private const string QElementName = "Q";

	private const string GElementName = "G";

	private const string JElementName = "J";

	private const string YElementName = "Y";

	private const string SeedElementName = "Seed";

	private const string PgenCounterElementName = "PgenCounter";

	public DSA Key
	{
		get
		{
			return _key;
		}
		set
		{
			_key = value;
		}
	}

	[UnsupportedOSPlatform("ios")]
	[UnsupportedOSPlatform("tvos")]
	public DSAKeyValue()
	{
		_key = DSA.Create();
	}

	public DSAKeyValue(DSA key)
	{
		_key = key;
	}

	public override XmlElement GetXml()
	{
		XmlDocument xmlDocument = new XmlDocument();
		xmlDocument.PreserveWhitespace = true;
		return GetXml(xmlDocument);
	}

	internal override XmlElement GetXml(XmlDocument xmlDocument)
	{
		DSAParameters dSAParameters = _key.ExportParameters(includePrivateParameters: false);
		XmlElement xmlElement = xmlDocument.CreateElement("KeyValue", "http://www.w3.org/2000/09/xmldsig#");
		XmlElement xmlElement2 = xmlDocument.CreateElement("DSAKeyValue", "http://www.w3.org/2000/09/xmldsig#");
		XmlElement xmlElement3 = xmlDocument.CreateElement("P", "http://www.w3.org/2000/09/xmldsig#");
		xmlElement3.AppendChild(xmlDocument.CreateTextNode(Convert.ToBase64String(dSAParameters.P)));
		xmlElement2.AppendChild(xmlElement3);
		XmlElement xmlElement4 = xmlDocument.CreateElement("Q", "http://www.w3.org/2000/09/xmldsig#");
		xmlElement4.AppendChild(xmlDocument.CreateTextNode(Convert.ToBase64String(dSAParameters.Q)));
		xmlElement2.AppendChild(xmlElement4);
		XmlElement xmlElement5 = xmlDocument.CreateElement("G", "http://www.w3.org/2000/09/xmldsig#");
		xmlElement5.AppendChild(xmlDocument.CreateTextNode(Convert.ToBase64String(dSAParameters.G)));
		xmlElement2.AppendChild(xmlElement5);
		XmlElement xmlElement6 = xmlDocument.CreateElement("Y", "http://www.w3.org/2000/09/xmldsig#");
		xmlElement6.AppendChild(xmlDocument.CreateTextNode(Convert.ToBase64String(dSAParameters.Y)));
		xmlElement2.AppendChild(xmlElement6);
		if (dSAParameters.J != null)
		{
			XmlElement xmlElement7 = xmlDocument.CreateElement("J", "http://www.w3.org/2000/09/xmldsig#");
			xmlElement7.AppendChild(xmlDocument.CreateTextNode(Convert.ToBase64String(dSAParameters.J)));
			xmlElement2.AppendChild(xmlElement7);
		}
		if (dSAParameters.Seed != null)
		{
			XmlElement xmlElement8 = xmlDocument.CreateElement("Seed", "http://www.w3.org/2000/09/xmldsig#");
			xmlElement8.AppendChild(xmlDocument.CreateTextNode(Convert.ToBase64String(dSAParameters.Seed)));
			xmlElement2.AppendChild(xmlElement8);
			XmlElement xmlElement9 = xmlDocument.CreateElement("PgenCounter", "http://www.w3.org/2000/09/xmldsig#");
			xmlElement9.AppendChild(xmlDocument.CreateTextNode(Convert.ToBase64String(Utils.ConvertIntToByteArray(dSAParameters.Counter))));
			xmlElement2.AppendChild(xmlElement9);
		}
		xmlElement.AppendChild(xmlElement2);
		return xmlElement;
	}

	public override void LoadXml(XmlElement value)
	{
		if (value == null)
		{
			throw new ArgumentNullException("value");
		}
		if (value.Name != "KeyValue" || value.NamespaceURI != "http://www.w3.org/2000/09/xmldsig#")
		{
			throw new CryptographicException(System.SR.Format(System.SR.WrongRootElement, "KeyValue", "http://www.w3.org/2000/09/xmldsig#"));
		}
		XmlNamespaceManager xmlNamespaceManager = new XmlNamespaceManager(value.OwnerDocument.NameTable);
		xmlNamespaceManager.AddNamespace("dsig", "http://www.w3.org/2000/09/xmldsig#");
		XmlNode xmlNode = value.SelectSingleNode("dsig:DSAKeyValue", xmlNamespaceManager);
		if (xmlNode == null)
		{
			throw new CryptographicException(System.SR.Format(System.SR.MustContainChildElement, "KeyValue", "DSAKeyValue"));
		}
		XmlNode xmlNode2 = xmlNode.SelectSingleNode("dsig:Y", xmlNamespaceManager);
		if (xmlNode2 == null)
		{
			throw new CryptographicException(System.SR.Format(System.SR.ElementMissing, "Y"));
		}
		XmlNode xmlNode3 = xmlNode.SelectSingleNode("dsig:P", xmlNamespaceManager);
		XmlNode xmlNode4 = xmlNode.SelectSingleNode("dsig:Q", xmlNamespaceManager);
		if ((xmlNode3 == null && xmlNode4 != null) || (xmlNode3 != null && xmlNode4 == null))
		{
			throw new CryptographicException(System.SR.Format(System.SR.ElementCombinationMissing, "P", "Q"));
		}
		XmlNode xmlNode5 = xmlNode.SelectSingleNode("dsig:G", xmlNamespaceManager);
		XmlNode xmlNode6 = xmlNode.SelectSingleNode("dsig:J", xmlNamespaceManager);
		XmlNode xmlNode7 = xmlNode.SelectSingleNode("dsig:Seed", xmlNamespaceManager);
		XmlNode xmlNode8 = xmlNode.SelectSingleNode("dsig:PgenCounter", xmlNamespaceManager);
		if ((xmlNode7 == null && xmlNode8 != null) || (xmlNode7 != null && xmlNode8 == null))
		{
			throw new CryptographicException(System.SR.Format(System.SR.ElementCombinationMissing, "Seed", "PgenCounter"));
		}
		try
		{
			Key.ImportParameters(new DSAParameters
			{
				P = ((xmlNode3 != null) ? Convert.FromBase64String(xmlNode3.InnerText) : null),
				Q = ((xmlNode4 != null) ? Convert.FromBase64String(xmlNode4.InnerText) : null),
				G = ((xmlNode5 != null) ? Convert.FromBase64String(xmlNode5.InnerText) : null),
				Y = Convert.FromBase64String(xmlNode2.InnerText),
				J = ((xmlNode6 != null) ? Convert.FromBase64String(xmlNode6.InnerText) : null),
				Seed = ((xmlNode7 != null) ? Convert.FromBase64String(xmlNode7.InnerText) : null),
				Counter = ((xmlNode8 != null) ? Utils.ConvertByteArrayToInt(Convert.FromBase64String(xmlNode8.InnerText)) : 0)
			});
		}
		catch (Exception inner)
		{
			throw new CryptographicException("An error occurred parsing the key components", inner);
		}
	}
}
