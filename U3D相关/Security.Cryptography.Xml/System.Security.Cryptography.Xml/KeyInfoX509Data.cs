using System.Collections;
using System.Globalization;
using System.Numerics;
using System.Security.Cryptography.X509Certificates;
using System.Xml;

namespace System.Security.Cryptography.Xml;

public class KeyInfoX509Data : KeyInfoClause
{
	private ArrayList _certificates;

	private ArrayList _issuerSerials;

	private ArrayList _subjectKeyIds;

	private ArrayList _subjectNames;

	private byte[] _CRL;

	public ArrayList Certificates => _certificates;

	public ArrayList SubjectKeyIds => _subjectKeyIds;

	public ArrayList SubjectNames => _subjectNames;

	public ArrayList IssuerSerials => _issuerSerials;

	public byte[] CRL
	{
		get
		{
			return _CRL;
		}
		set
		{
			_CRL = value;
		}
	}

	public KeyInfoX509Data()
	{
	}

	public KeyInfoX509Data(byte[] rgbCert)
	{
		X509Certificate2 certificate = new X509Certificate2(rgbCert);
		AddCertificate(certificate);
	}

	public KeyInfoX509Data(X509Certificate cert)
	{
		AddCertificate(cert);
	}

	public KeyInfoX509Data(X509Certificate cert, X509IncludeOption includeOption)
	{
		if (cert == null)
		{
			throw new ArgumentNullException("cert");
		}
		X509Certificate2 certificate = new X509Certificate2(cert);
		switch (includeOption)
		{
		case X509IncludeOption.ExcludeRoot:
		{
			X509Chain x509Chain = new X509Chain();
			x509Chain.Build(certificate);
			if (x509Chain.ChainStatus.Length != 0 && (x509Chain.ChainStatus[0].Status & X509ChainStatusFlags.PartialChain) == X509ChainStatusFlags.PartialChain)
			{
				throw new CryptographicException(System.SR.Cryptography_Partial_Chain);
			}
			X509ChainElementCollection chainElements = x509Chain.ChainElements;
			for (int i = 0; i < (Utils.IsSelfSigned(x509Chain) ? 1 : (chainElements.Count - 1)); i++)
			{
				AddCertificate(chainElements[i].Certificate);
			}
			break;
		}
		case X509IncludeOption.EndCertOnly:
			AddCertificate(certificate);
			break;
		case X509IncludeOption.WholeChain:
		{
			X509Chain x509Chain = new X509Chain();
			x509Chain.Build(certificate);
			if (x509Chain.ChainStatus.Length != 0 && (x509Chain.ChainStatus[0].Status & X509ChainStatusFlags.PartialChain) == X509ChainStatusFlags.PartialChain)
			{
				throw new CryptographicException(System.SR.Cryptography_Partial_Chain);
			}
			X509ChainElementCollection chainElements = x509Chain.ChainElements;
			X509ChainElementEnumerator enumerator = chainElements.GetEnumerator();
			while (enumerator.MoveNext())
			{
				X509ChainElement current = enumerator.Current;
				AddCertificate(current.Certificate);
			}
			break;
		}
		}
	}

	public void AddCertificate(X509Certificate certificate)
	{
		if (certificate == null)
		{
			throw new ArgumentNullException("certificate");
		}
		if (_certificates == null)
		{
			_certificates = new ArrayList();
		}
		X509Certificate2 value = new X509Certificate2(certificate);
		_certificates.Add(value);
	}

	public void AddSubjectKeyId(byte[] subjectKeyId)
	{
		if (_subjectKeyIds == null)
		{
			_subjectKeyIds = new ArrayList();
		}
		_subjectKeyIds.Add(subjectKeyId);
	}

	public void AddSubjectKeyId(string subjectKeyId)
	{
		if (_subjectKeyIds == null)
		{
			_subjectKeyIds = new ArrayList();
		}
		_subjectKeyIds.Add(Utils.DecodeHexString(subjectKeyId));
	}

	public void AddSubjectName(string subjectName)
	{
		if (_subjectNames == null)
		{
			_subjectNames = new ArrayList();
		}
		_subjectNames.Add(subjectName);
	}

	public void AddIssuerSerial(string issuerName, string serialNumber)
	{
		if (string.IsNullOrEmpty(issuerName))
		{
			throw new ArgumentException(System.SR.Arg_EmptyOrNullString, "issuerName");
		}
		if (string.IsNullOrEmpty(serialNumber))
		{
			throw new ArgumentException(System.SR.Arg_EmptyOrNullString, "serialNumber");
		}
		if (!BigInteger.TryParse(serialNumber, NumberStyles.AllowHexSpecifier, NumberFormatInfo.CurrentInfo, out var result))
		{
			throw new ArgumentException(System.SR.Cryptography_Xml_InvalidX509IssuerSerialNumber, "serialNumber");
		}
		if (_issuerSerials == null)
		{
			_issuerSerials = new ArrayList();
		}
		_issuerSerials.Add(Utils.CreateX509IssuerSerial(issuerName, result.ToString()));
	}

	internal void InternalAddIssuerSerial(string issuerName, string serialNumber)
	{
		if (_issuerSerials == null)
		{
			_issuerSerials = new ArrayList();
		}
		_issuerSerials.Add(Utils.CreateX509IssuerSerial(issuerName, serialNumber));
	}

	private void Clear()
	{
		_CRL = null;
		_subjectKeyIds?.Clear();
		_subjectNames?.Clear();
		_issuerSerials?.Clear();
		_certificates?.Clear();
	}

	public override XmlElement GetXml()
	{
		XmlDocument xmlDocument = new XmlDocument();
		xmlDocument.PreserveWhitespace = true;
		return GetXml(xmlDocument);
	}

	internal override XmlElement GetXml(XmlDocument xmlDocument)
	{
		XmlElement xmlElement = xmlDocument.CreateElement("X509Data", "http://www.w3.org/2000/09/xmldsig#");
		if (_issuerSerials != null)
		{
			foreach (X509IssuerSerial issuerSerial in _issuerSerials)
			{
				XmlElement xmlElement2 = xmlDocument.CreateElement("X509IssuerSerial", "http://www.w3.org/2000/09/xmldsig#");
				XmlElement xmlElement3 = xmlDocument.CreateElement("X509IssuerName", "http://www.w3.org/2000/09/xmldsig#");
				xmlElement3.AppendChild(xmlDocument.CreateTextNode(issuerSerial.IssuerName));
				xmlElement2.AppendChild(xmlElement3);
				XmlElement xmlElement4 = xmlDocument.CreateElement("X509SerialNumber", "http://www.w3.org/2000/09/xmldsig#");
				xmlElement4.AppendChild(xmlDocument.CreateTextNode(issuerSerial.SerialNumber));
				xmlElement2.AppendChild(xmlElement4);
				xmlElement.AppendChild(xmlElement2);
			}
		}
		if (_subjectKeyIds != null)
		{
			foreach (byte[] subjectKeyId in _subjectKeyIds)
			{
				XmlElement xmlElement5 = xmlDocument.CreateElement("X509SKI", "http://www.w3.org/2000/09/xmldsig#");
				xmlElement5.AppendChild(xmlDocument.CreateTextNode(Convert.ToBase64String(subjectKeyId)));
				xmlElement.AppendChild(xmlElement5);
			}
		}
		if (_subjectNames != null)
		{
			foreach (string subjectName in _subjectNames)
			{
				XmlElement xmlElement6 = xmlDocument.CreateElement("X509SubjectName", "http://www.w3.org/2000/09/xmldsig#");
				xmlElement6.AppendChild(xmlDocument.CreateTextNode(subjectName));
				xmlElement.AppendChild(xmlElement6);
			}
		}
		if (_certificates != null)
		{
			foreach (X509Certificate certificate in _certificates)
			{
				XmlElement xmlElement7 = xmlDocument.CreateElement("X509Certificate", "http://www.w3.org/2000/09/xmldsig#");
				xmlElement7.AppendChild(xmlDocument.CreateTextNode(Convert.ToBase64String(certificate.GetRawCertData())));
				xmlElement.AppendChild(xmlElement7);
			}
		}
		if (_CRL != null)
		{
			XmlElement xmlElement8 = xmlDocument.CreateElement("X509CRL", "http://www.w3.org/2000/09/xmldsig#");
			xmlElement8.AppendChild(xmlDocument.CreateTextNode(Convert.ToBase64String(_CRL)));
			xmlElement.AppendChild(xmlElement8);
		}
		return xmlElement;
	}

	public override void LoadXml(XmlElement element)
	{
		if (element == null)
		{
			throw new ArgumentNullException("element");
		}
		XmlNamespaceManager xmlNamespaceManager = new XmlNamespaceManager(element.OwnerDocument.NameTable);
		xmlNamespaceManager.AddNamespace("ds", "http://www.w3.org/2000/09/xmldsig#");
		XmlNodeList xmlNodeList = element.SelectNodes("ds:X509IssuerSerial", xmlNamespaceManager);
		XmlNodeList xmlNodeList2 = element.SelectNodes("ds:X509SKI", xmlNamespaceManager);
		XmlNodeList xmlNodeList3 = element.SelectNodes("ds:X509SubjectName", xmlNamespaceManager);
		XmlNodeList xmlNodeList4 = element.SelectNodes("ds:X509Certificate", xmlNamespaceManager);
		XmlNodeList xmlNodeList5 = element.SelectNodes("ds:X509CRL", xmlNamespaceManager);
		if (xmlNodeList5.Count == 0 && xmlNodeList.Count == 0 && xmlNodeList2.Count == 0 && xmlNodeList3.Count == 0 && xmlNodeList4.Count == 0)
		{
			throw new CryptographicException(System.SR.Cryptography_Xml_InvalidElement, "X509Data");
		}
		Clear();
		if (xmlNodeList5.Count != 0)
		{
			_CRL = Convert.FromBase64String(Utils.DiscardWhiteSpaces(xmlNodeList5.Item(0).InnerText));
		}
		foreach (XmlNode item in xmlNodeList)
		{
			XmlNode xmlNode2 = item.SelectSingleNode("ds:X509IssuerName", xmlNamespaceManager);
			XmlNode xmlNode3 = item.SelectSingleNode("ds:X509SerialNumber", xmlNamespaceManager);
			if (xmlNode2 == null || xmlNode3 == null)
			{
				throw new CryptographicException(System.SR.Cryptography_Xml_InvalidElement, "IssuerSerial");
			}
			InternalAddIssuerSerial(xmlNode2.InnerText.Trim(), xmlNode3.InnerText.Trim());
		}
		foreach (XmlNode item2 in xmlNodeList2)
		{
			AddSubjectKeyId(Convert.FromBase64String(Utils.DiscardWhiteSpaces(item2.InnerText)));
		}
		foreach (XmlNode item3 in xmlNodeList3)
		{
			AddSubjectName(item3.InnerText.Trim());
		}
		foreach (XmlNode item4 in xmlNodeList4)
		{
			AddCertificate(new X509Certificate2(Convert.FromBase64String(Utils.DiscardWhiteSpaces(item4.InnerText))));
		}
	}
}
