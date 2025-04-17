using System.Collections;
using System.Xml;

namespace System.Security.Cryptography.Xml;

public class Signature
{
	private string _id;

	private SignedInfo _signedInfo;

	private byte[] _signatureValue;

	private string _signatureValueId;

	private KeyInfo _keyInfo;

	private IList _embeddedObjects;

	private readonly CanonicalXmlNodeList _referencedItems;

	private SignedXml _signedXml;

	internal SignedXml SignedXml
	{
		get
		{
			return _signedXml;
		}
		set
		{
			_signedXml = value;
		}
	}

	public string Id
	{
		get
		{
			return _id;
		}
		set
		{
			_id = value;
		}
	}

	public SignedInfo SignedInfo
	{
		get
		{
			return _signedInfo;
		}
		set
		{
			_signedInfo = value;
			if (SignedXml != null && _signedInfo != null)
			{
				_signedInfo.SignedXml = SignedXml;
			}
		}
	}

	public byte[] SignatureValue
	{
		get
		{
			return _signatureValue;
		}
		set
		{
			_signatureValue = value;
		}
	}

	public KeyInfo KeyInfo
	{
		get
		{
			return _keyInfo ?? (_keyInfo = new KeyInfo());
		}
		set
		{
			_keyInfo = value;
		}
	}

	public IList ObjectList
	{
		get
		{
			return _embeddedObjects;
		}
		set
		{
			_embeddedObjects = value;
		}
	}

	internal CanonicalXmlNodeList ReferencedItems => _referencedItems;

	public Signature()
	{
		_embeddedObjects = new ArrayList();
		_referencedItems = new CanonicalXmlNodeList();
	}

	public XmlElement GetXml()
	{
		XmlDocument xmlDocument = new XmlDocument();
		xmlDocument.PreserveWhitespace = true;
		return GetXml(xmlDocument);
	}

	internal XmlElement GetXml(XmlDocument document)
	{
		XmlElement xmlElement = document.CreateElement("Signature", "http://www.w3.org/2000/09/xmldsig#");
		if (!string.IsNullOrEmpty(_id))
		{
			xmlElement.SetAttribute("Id", _id);
		}
		if (_signedInfo == null)
		{
			throw new CryptographicException(System.SR.Cryptography_Xml_SignedInfoRequired);
		}
		xmlElement.AppendChild(_signedInfo.GetXml(document));
		if (_signatureValue == null)
		{
			throw new CryptographicException(System.SR.Cryptography_Xml_SignatureValueRequired);
		}
		XmlElement xmlElement2 = document.CreateElement("SignatureValue", "http://www.w3.org/2000/09/xmldsig#");
		xmlElement2.AppendChild(document.CreateTextNode(Convert.ToBase64String(_signatureValue)));
		if (!string.IsNullOrEmpty(_signatureValueId))
		{
			xmlElement2.SetAttribute("Id", _signatureValueId);
		}
		xmlElement.AppendChild(xmlElement2);
		if (KeyInfo.Count > 0)
		{
			xmlElement.AppendChild(KeyInfo.GetXml(document));
		}
		foreach (object embeddedObject in _embeddedObjects)
		{
			if (embeddedObject is DataObject dataObject)
			{
				xmlElement.AppendChild(dataObject.GetXml(document));
			}
		}
		return xmlElement;
	}

	public void LoadXml(XmlElement value)
	{
		if (value == null)
		{
			throw new ArgumentNullException("value");
		}
		if (!value.LocalName.Equals("Signature"))
		{
			throw new CryptographicException(System.SR.Cryptography_Xml_InvalidElement, "Signature");
		}
		_id = Utils.GetAttribute(value, "Id", "http://www.w3.org/2000/09/xmldsig#");
		if (!Utils.VerifyAttributes(value, "Id"))
		{
			throw new CryptographicException(System.SR.Cryptography_Xml_InvalidElement, "Signature");
		}
		XmlNamespaceManager xmlNamespaceManager = new XmlNamespaceManager(value.OwnerDocument.NameTable);
		xmlNamespaceManager.AddNamespace("ds", "http://www.w3.org/2000/09/xmldsig#");
		int num = 0;
		XmlNodeList xmlNodeList = value.SelectNodes("ds:SignedInfo", xmlNamespaceManager);
		if (xmlNodeList == null || xmlNodeList.Count == 0 || xmlNodeList.Count > 1)
		{
			throw new CryptographicException(System.SR.Cryptography_Xml_InvalidElement, "SignedInfo");
		}
		XmlElement value2 = xmlNodeList[0] as XmlElement;
		num += xmlNodeList.Count;
		SignedInfo = new SignedInfo();
		SignedInfo.LoadXml(value2);
		XmlNodeList xmlNodeList2 = value.SelectNodes("ds:SignatureValue", xmlNamespaceManager);
		if (xmlNodeList2 == null || xmlNodeList2.Count == 0 || xmlNodeList2.Count > 1)
		{
			throw new CryptographicException(System.SR.Cryptography_Xml_InvalidElement, "SignatureValue");
		}
		XmlElement xmlElement = xmlNodeList2[0] as XmlElement;
		num += xmlNodeList2.Count;
		_signatureValue = Convert.FromBase64String(Utils.DiscardWhiteSpaces(xmlElement.InnerText));
		_signatureValueId = Utils.GetAttribute(xmlElement, "Id", "http://www.w3.org/2000/09/xmldsig#");
		if (!Utils.VerifyAttributes(xmlElement, "Id"))
		{
			throw new CryptographicException(System.SR.Cryptography_Xml_InvalidElement, "SignatureValue");
		}
		XmlNodeList xmlNodeList3 = value.SelectNodes("ds:KeyInfo", xmlNamespaceManager);
		_keyInfo = new KeyInfo();
		if (xmlNodeList3 != null)
		{
			if (xmlNodeList3.Count > 1)
			{
				throw new CryptographicException(System.SR.Cryptography_Xml_InvalidElement, "KeyInfo");
			}
			foreach (XmlNode item in xmlNodeList3)
			{
				if (item is XmlElement value3)
				{
					_keyInfo.LoadXml(value3);
				}
			}
			num += xmlNodeList3.Count;
		}
		XmlNodeList xmlNodeList4 = value.SelectNodes("ds:Object", xmlNamespaceManager);
		_embeddedObjects.Clear();
		if (xmlNodeList4 != null)
		{
			foreach (XmlNode item2 in xmlNodeList4)
			{
				if (item2 is XmlElement value4)
				{
					DataObject dataObject = new DataObject();
					dataObject.LoadXml(value4);
					_embeddedObjects.Add(dataObject);
				}
			}
			num += xmlNodeList4.Count;
		}
		XmlNodeList xmlNodeList5 = value.SelectNodes("//*[@Id]", xmlNamespaceManager);
		if (xmlNodeList5 != null)
		{
			foreach (XmlNode item3 in xmlNodeList5)
			{
				_referencedItems.Add(item3);
			}
		}
		if (value.SelectNodes("*").Count != num)
		{
			throw new CryptographicException(System.SR.Cryptography_Xml_InvalidElement, "Signature");
		}
	}

	public void AddObject(DataObject dataObject)
	{
		_embeddedObjects.Add(dataObject);
	}
}
