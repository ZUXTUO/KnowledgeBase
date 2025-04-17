using System.Collections;
using System.Xml;

namespace System.Security.Cryptography.Xml;

public class SignedInfo : ICollection, IEnumerable
{
	private string _id;

	private string _canonicalizationMethod;

	private string _signatureMethod;

	private string _signatureLength;

	private readonly ArrayList _references;

	private XmlElement _cachedXml;

	private SignedXml _signedXml;

	private Transform _canonicalizationMethodTransform;

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

	public int Count
	{
		get
		{
			throw new NotSupportedException();
		}
	}

	public bool IsReadOnly
	{
		get
		{
			throw new NotSupportedException();
		}
	}

	public bool IsSynchronized
	{
		get
		{
			throw new NotSupportedException();
		}
	}

	public object SyncRoot
	{
		get
		{
			throw new NotSupportedException();
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
			_cachedXml = null;
		}
	}

	public string CanonicalizationMethod
	{
		get
		{
			if (_canonicalizationMethod == null)
			{
				return "http://www.w3.org/TR/2001/REC-xml-c14n-20010315";
			}
			return _canonicalizationMethod;
		}
		set
		{
			_canonicalizationMethod = value;
			_cachedXml = null;
		}
	}

	public Transform CanonicalizationMethodObject
	{
		get
		{
			if (_canonicalizationMethodTransform == null)
			{
				_canonicalizationMethodTransform = CryptoHelpers.CreateFromName<Transform>(CanonicalizationMethod);
				if (_canonicalizationMethodTransform == null)
				{
					throw new CryptographicException(System.SR.Format(System.SR.Cryptography_Xml_CreateTransformFailed, CanonicalizationMethod));
				}
				_canonicalizationMethodTransform.SignedXml = SignedXml;
				_canonicalizationMethodTransform.Reference = null;
			}
			return _canonicalizationMethodTransform;
		}
	}

	public string SignatureMethod
	{
		get
		{
			return _signatureMethod;
		}
		set
		{
			_signatureMethod = value;
			_cachedXml = null;
		}
	}

	public string SignatureLength
	{
		get
		{
			return _signatureLength;
		}
		set
		{
			_signatureLength = value;
			_cachedXml = null;
		}
	}

	public ArrayList References => _references;

	internal bool CacheValid
	{
		get
		{
			if (_cachedXml == null)
			{
				return false;
			}
			foreach (Reference reference in References)
			{
				if (!reference.CacheValid)
				{
					return false;
				}
			}
			return true;
		}
	}

	public SignedInfo()
	{
		_references = new ArrayList();
	}

	public IEnumerator GetEnumerator()
	{
		throw new NotSupportedException();
	}

	public void CopyTo(Array array, int index)
	{
		throw new NotSupportedException();
	}

	public XmlElement GetXml()
	{
		if (CacheValid)
		{
			return _cachedXml;
		}
		XmlDocument xmlDocument = new XmlDocument();
		xmlDocument.PreserveWhitespace = true;
		return GetXml(xmlDocument);
	}

	internal XmlElement GetXml(XmlDocument document)
	{
		XmlElement xmlElement = document.CreateElement("SignedInfo", "http://www.w3.org/2000/09/xmldsig#");
		if (!string.IsNullOrEmpty(_id))
		{
			xmlElement.SetAttribute("Id", _id);
		}
		XmlElement xml = CanonicalizationMethodObject.GetXml(document, "CanonicalizationMethod");
		xmlElement.AppendChild(xml);
		if (string.IsNullOrEmpty(_signatureMethod))
		{
			throw new CryptographicException(System.SR.Cryptography_Xml_SignatureMethodRequired);
		}
		XmlElement xmlElement2 = document.CreateElement("SignatureMethod", "http://www.w3.org/2000/09/xmldsig#");
		xmlElement2.SetAttribute("Algorithm", _signatureMethod);
		if (_signatureLength != null)
		{
			XmlElement xmlElement3 = document.CreateElement(null, "HMACOutputLength", "http://www.w3.org/2000/09/xmldsig#");
			XmlText newChild = document.CreateTextNode(_signatureLength);
			xmlElement3.AppendChild(newChild);
			xmlElement2.AppendChild(xmlElement3);
		}
		xmlElement.AppendChild(xmlElement2);
		if (_references.Count == 0)
		{
			throw new CryptographicException(System.SR.Cryptography_Xml_ReferenceElementRequired);
		}
		for (int i = 0; i < _references.Count; i++)
		{
			Reference reference = (Reference)_references[i];
			xmlElement.AppendChild(reference.GetXml(document));
		}
		return xmlElement;
	}

	public void LoadXml(XmlElement value)
	{
		if (value == null)
		{
			throw new ArgumentNullException("value");
		}
		if (!value.LocalName.Equals("SignedInfo"))
		{
			throw new CryptographicException(System.SR.Cryptography_Xml_InvalidElement, "SignedInfo");
		}
		XmlNamespaceManager xmlNamespaceManager = new XmlNamespaceManager(value.OwnerDocument.NameTable);
		xmlNamespaceManager.AddNamespace("ds", "http://www.w3.org/2000/09/xmldsig#");
		int num = 0;
		_id = Utils.GetAttribute(value, "Id", "http://www.w3.org/2000/09/xmldsig#");
		if (!Utils.VerifyAttributes(value, "Id"))
		{
			throw new CryptographicException(System.SR.Cryptography_Xml_InvalidElement, "SignedInfo");
		}
		XmlNodeList xmlNodeList = value.SelectNodes("ds:CanonicalizationMethod", xmlNamespaceManager);
		if (xmlNodeList == null || xmlNodeList.Count == 0 || xmlNodeList.Count > 1)
		{
			throw new CryptographicException(System.SR.Cryptography_Xml_InvalidElement, "SignedInfo/CanonicalizationMethod");
		}
		XmlElement xmlElement = xmlNodeList.Item(0) as XmlElement;
		num += xmlNodeList.Count;
		_canonicalizationMethod = Utils.GetAttribute(xmlElement, "Algorithm", "http://www.w3.org/2000/09/xmldsig#");
		if (_canonicalizationMethod == null || !Utils.VerifyAttributes(xmlElement, "Algorithm"))
		{
			throw new CryptographicException(System.SR.Cryptography_Xml_InvalidElement, "SignedInfo/CanonicalizationMethod");
		}
		_canonicalizationMethodTransform = null;
		if (xmlElement.ChildNodes.Count > 0)
		{
			CanonicalizationMethodObject.LoadInnerXml(xmlElement.ChildNodes);
		}
		XmlNodeList xmlNodeList2 = value.SelectNodes("ds:SignatureMethod", xmlNamespaceManager);
		if (xmlNodeList2 == null || xmlNodeList2.Count == 0 || xmlNodeList2.Count > 1)
		{
			throw new CryptographicException(System.SR.Cryptography_Xml_InvalidElement, "SignedInfo/SignatureMethod");
		}
		XmlElement xmlElement2 = xmlNodeList2.Item(0) as XmlElement;
		num += xmlNodeList2.Count;
		_signatureMethod = Utils.GetAttribute(xmlElement2, "Algorithm", "http://www.w3.org/2000/09/xmldsig#");
		if (_signatureMethod == null || !Utils.VerifyAttributes(xmlElement2, "Algorithm"))
		{
			throw new CryptographicException(System.SR.Cryptography_Xml_InvalidElement, "SignedInfo/SignatureMethod");
		}
		if (xmlElement2.SelectSingleNode("ds:HMACOutputLength", xmlNamespaceManager) is XmlElement xmlElement3)
		{
			_signatureLength = xmlElement3.InnerXml;
		}
		_references.Clear();
		XmlNodeList xmlNodeList3 = value.SelectNodes("ds:Reference", xmlNamespaceManager);
		if (xmlNodeList3 != null)
		{
			if (xmlNodeList3.Count > 100)
			{
				throw new CryptographicException(System.SR.Cryptography_Xml_InvalidElement, "SignedInfo/Reference");
			}
			foreach (XmlNode item in xmlNodeList3)
			{
				XmlElement value2 = item as XmlElement;
				Reference reference = new Reference();
				AddReference(reference);
				reference.LoadXml(value2);
			}
			num += xmlNodeList3.Count;
			if (value.SelectNodes("*").Count != num)
			{
				throw new CryptographicException(System.SR.Cryptography_Xml_InvalidElement, "SignedInfo");
			}
		}
		_cachedXml = value;
	}

	public void AddReference(Reference reference)
	{
		if (reference == null)
		{
			throw new ArgumentNullException("reference");
		}
		reference.SignedXml = SignedXml;
		_references.Add(reference);
	}
}
