using System.Collections;
using System.IO;
using System.Security.Cryptography.X509Certificates;
using System.Security.Cryptography.Xml;
using System.Text;
using System.Xml;

namespace System.Security.Cryptography.Xml;

internal static class Utils
{
	internal const int MaxCharactersInDocument = 0;

	internal const long MaxCharactersFromEntities = 10000000L;

	internal const int XmlDsigSearchDepth = 20;

	internal const int MaxTransformsPerReference = 10;

	internal const int MaxReferencesPerSignedInfo = 100;

	private static bool HasNamespace(XmlElement element, string prefix, string value)
	{
		if (IsCommittedNamespace(element, prefix, value))
		{
			return true;
		}
		if (element.Prefix == prefix && element.NamespaceURI == value)
		{
			return true;
		}
		return false;
	}

	internal static bool IsCommittedNamespace(XmlElement element, string prefix, string value)
	{
		if (element == null)
		{
			throw new ArgumentNullException("element");
		}
		string name = ((prefix.Length > 0) ? ("xmlns:" + prefix) : "xmlns");
		if (element.HasAttribute(name) && element.GetAttribute(name) == value)
		{
			return true;
		}
		return false;
	}

	internal static bool IsRedundantNamespace(XmlElement element, string prefix, string value)
	{
		if (element == null)
		{
			throw new ArgumentNullException("element");
		}
		for (XmlNode parentNode = element.ParentNode; parentNode != null; parentNode = parentNode.ParentNode)
		{
			if (parentNode is XmlElement element2 && HasNamespace(element2, prefix, value))
			{
				return true;
			}
		}
		return false;
	}

	internal static string GetAttribute(XmlElement element, string localName, string namespaceURI)
	{
		string text = (element.HasAttribute(localName) ? element.GetAttribute(localName) : null);
		if (text == null && element.HasAttribute(localName, namespaceURI))
		{
			text = element.GetAttribute(localName, namespaceURI);
		}
		return text;
	}

	internal static bool HasAttribute(XmlElement element, string localName, string namespaceURI)
	{
		if (!element.HasAttribute(localName))
		{
			return element.HasAttribute(localName, namespaceURI);
		}
		return true;
	}

	internal static bool VerifyAttributes(XmlElement element, string expectedAttrName)
	{
		return VerifyAttributes(element, (expectedAttrName == null) ? null : new string[1] { expectedAttrName });
	}

	internal static bool VerifyAttributes(XmlElement element, string[] expectedAttrNames)
	{
		foreach (XmlAttribute attribute in element.Attributes)
		{
			bool flag = attribute.Name == "xmlns" || attribute.Name.StartsWith("xmlns:") || attribute.Name == "xml:space" || attribute.Name == "xml:lang" || attribute.Name == "xml:base";
			int num = 0;
			while (!flag && expectedAttrNames != null && num < expectedAttrNames.Length)
			{
				flag = attribute.Name == expectedAttrNames[num];
				num++;
			}
			if (!flag)
			{
				return false;
			}
		}
		return true;
	}

	internal static bool IsNamespaceNode(XmlNode n)
	{
		if (n.NodeType == XmlNodeType.Attribute)
		{
			if (!n.Prefix.Equals("xmlns"))
			{
				if (n.Prefix.Length == 0)
				{
					return n.LocalName.Equals("xmlns");
				}
				return false;
			}
			return true;
		}
		return false;
	}

	internal static bool IsXmlNamespaceNode(XmlNode n)
	{
		if (n.NodeType == XmlNodeType.Attribute)
		{
			return n.Prefix.Equals("xml");
		}
		return false;
	}

	internal static bool IsDefaultNamespaceNode(XmlNode n)
	{
		bool flag = n.NodeType == XmlNodeType.Attribute && n.Prefix.Length == 0 && n.LocalName.Equals("xmlns");
		bool flag2 = IsXmlNamespaceNode(n);
		return flag || flag2;
	}

	internal static bool IsEmptyDefaultNamespaceNode(XmlNode n)
	{
		if (IsDefaultNamespaceNode(n))
		{
			return n.Value.Length == 0;
		}
		return false;
	}

	internal static string GetNamespacePrefix(XmlAttribute a)
	{
		if (a.Prefix.Length != 0)
		{
			return a.LocalName;
		}
		return string.Empty;
	}

	internal static bool HasNamespacePrefix(XmlAttribute a, string nsPrefix)
	{
		return GetNamespacePrefix(a).Equals(nsPrefix);
	}

	internal static bool IsNonRedundantNamespaceDecl(XmlAttribute a, XmlAttribute nearestAncestorWithSamePrefix)
	{
		if (nearestAncestorWithSamePrefix == null)
		{
			return !IsEmptyDefaultNamespaceNode(a);
		}
		return !nearestAncestorWithSamePrefix.Value.Equals(a.Value);
	}

	internal static bool IsXmlPrefixDefinitionNode(XmlAttribute a)
	{
		return false;
	}

	internal static string DiscardWhiteSpaces(string inputBuffer)
	{
		return DiscardWhiteSpaces(inputBuffer, 0, inputBuffer.Length);
	}

	internal static string DiscardWhiteSpaces(string inputBuffer, int inputOffset, int inputCount)
	{
		int num = 0;
		for (int i = 0; i < inputCount; i++)
		{
			if (char.IsWhiteSpace(inputBuffer[inputOffset + i]))
			{
				num++;
			}
		}
		char[] array = new char[inputCount - num];
		num = 0;
		for (int i = 0; i < inputCount; i++)
		{
			if (!char.IsWhiteSpace(inputBuffer[inputOffset + i]))
			{
				array[num++] = inputBuffer[inputOffset + i];
			}
		}
		return new string(array);
	}

	internal static void SBReplaceCharWithString(StringBuilder sb, char oldChar, string newString)
	{
		int num = 0;
		int length = newString.Length;
		while (num < sb.Length)
		{
			if (sb[num] == oldChar)
			{
				sb.Remove(num, 1);
				sb.Insert(num, newString);
				num += length;
			}
			else
			{
				num++;
			}
		}
	}

	internal static XmlReader PreProcessStreamInput(Stream inputStream, XmlResolver xmlResolver, string baseUri)
	{
		XmlReaderSettings secureXmlReaderSettings = GetSecureXmlReaderSettings(xmlResolver);
		return XmlReader.Create(inputStream, secureXmlReaderSettings, baseUri);
	}

	internal static XmlReaderSettings GetSecureXmlReaderSettings(XmlResolver xmlResolver)
	{
		XmlReaderSettings xmlReaderSettings = new XmlReaderSettings();
		xmlReaderSettings.XmlResolver = xmlResolver;
		xmlReaderSettings.DtdProcessing = DtdProcessing.Parse;
		xmlReaderSettings.MaxCharactersFromEntities = 10000000L;
		xmlReaderSettings.MaxCharactersInDocument = 0L;
		return xmlReaderSettings;
	}

	internal static XmlDocument PreProcessDocumentInput(XmlDocument document, XmlResolver xmlResolver, string baseUri)
	{
		if (document == null)
		{
			throw new ArgumentNullException("document");
		}
		MyXmlDocument myXmlDocument = new MyXmlDocument();
		myXmlDocument.PreserveWhitespace = document.PreserveWhitespace;
		using TextReader input = new StringReader(document.OuterXml);
		XmlReaderSettings xmlReaderSettings = new XmlReaderSettings();
		xmlReaderSettings.XmlResolver = xmlResolver;
		xmlReaderSettings.DtdProcessing = DtdProcessing.Parse;
		xmlReaderSettings.MaxCharactersFromEntities = 10000000L;
		xmlReaderSettings.MaxCharactersInDocument = 0L;
		XmlReader reader = XmlReader.Create(input, xmlReaderSettings, baseUri);
		myXmlDocument.Load(reader);
		return myXmlDocument;
	}

	internal static XmlDocument PreProcessElementInput(XmlElement elem, XmlResolver xmlResolver, string baseUri)
	{
		if (elem == null)
		{
			throw new ArgumentNullException("elem");
		}
		MyXmlDocument myXmlDocument = new MyXmlDocument();
		myXmlDocument.PreserveWhitespace = true;
		using TextReader input = new StringReader(elem.OuterXml);
		XmlReaderSettings xmlReaderSettings = new XmlReaderSettings();
		xmlReaderSettings.XmlResolver = xmlResolver;
		xmlReaderSettings.DtdProcessing = DtdProcessing.Parse;
		xmlReaderSettings.MaxCharactersFromEntities = 10000000L;
		xmlReaderSettings.MaxCharactersInDocument = 0L;
		XmlReader reader = XmlReader.Create(input, xmlReaderSettings, baseUri);
		myXmlDocument.Load(reader);
		return myXmlDocument;
	}

	internal static XmlDocument DiscardComments(XmlDocument document)
	{
		XmlNodeList xmlNodeList = document.SelectNodes("//comment()");
		if (xmlNodeList != null)
		{
			foreach (XmlNode item in xmlNodeList)
			{
				item.ParentNode.RemoveChild(item);
			}
		}
		return document;
	}

	internal static XmlNodeList AllDescendantNodes(XmlNode node, bool includeComments)
	{
		CanonicalXmlNodeList canonicalXmlNodeList = new CanonicalXmlNodeList();
		CanonicalXmlNodeList canonicalXmlNodeList2 = new CanonicalXmlNodeList();
		CanonicalXmlNodeList canonicalXmlNodeList3 = new CanonicalXmlNodeList();
		CanonicalXmlNodeList canonicalXmlNodeList4 = new CanonicalXmlNodeList();
		int num = 0;
		canonicalXmlNodeList2.Add(node);
		do
		{
			XmlNode xmlNode = canonicalXmlNodeList2[num];
			XmlNodeList childNodes = xmlNode.ChildNodes;
			if (childNodes != null)
			{
				foreach (XmlNode item in childNodes)
				{
					if (includeComments || !(item is XmlComment))
					{
						canonicalXmlNodeList2.Add(item);
					}
				}
			}
			XmlAttributeCollection attributes = xmlNode.Attributes;
			if (attributes != null)
			{
				foreach (XmlNode attribute in xmlNode.Attributes)
				{
					if (attribute.LocalName == "xmlns" || attribute.Prefix == "xmlns")
					{
						canonicalXmlNodeList4.Add(attribute);
					}
					else
					{
						canonicalXmlNodeList3.Add(attribute);
					}
				}
			}
			num++;
		}
		while (num < canonicalXmlNodeList2.Count);
		foreach (XmlNode item2 in canonicalXmlNodeList2)
		{
			canonicalXmlNodeList.Add(item2);
		}
		foreach (XmlNode item3 in canonicalXmlNodeList3)
		{
			canonicalXmlNodeList.Add(item3);
		}
		foreach (XmlNode item4 in canonicalXmlNodeList4)
		{
			canonicalXmlNodeList.Add(item4);
		}
		return canonicalXmlNodeList;
	}

	internal static bool NodeInList(XmlNode node, XmlNodeList nodeList)
	{
		foreach (XmlNode node2 in nodeList)
		{
			if (node2 == node)
			{
				return true;
			}
		}
		return false;
	}

	internal static string GetIdFromLocalUri(string uri, out bool discardComments)
	{
		string text = uri.Substring(1);
		discardComments = true;
		if (text.StartsWith("xpointer(id(", StringComparison.Ordinal))
		{
			int num = text.IndexOf("id(", StringComparison.Ordinal);
			int num2 = text.IndexOf(')');
			if (num2 < 0 || num2 < num + 3)
			{
				throw new CryptographicException(System.SR.Cryptography_Xml_InvalidReference);
			}
			text = text.Substring(num + 3, num2 - num - 3);
			text = text.Replace("'", "");
			text = text.Replace("\"", "");
			discardComments = false;
		}
		return text;
	}

	internal static string ExtractIdFromLocalUri(string uri)
	{
		string text = uri.Substring(1);
		if (text.StartsWith("xpointer(id(", StringComparison.Ordinal))
		{
			int num = text.IndexOf("id(", StringComparison.Ordinal);
			int num2 = text.IndexOf(')');
			if (num2 < 0 || num2 < num + 3)
			{
				throw new CryptographicException(System.SR.Cryptography_Xml_InvalidReference);
			}
			text = text.Substring(num + 3, num2 - num - 3);
			text = text.Replace("'", "");
			text = text.Replace("\"", "");
		}
		return text;
	}

	internal static void RemoveAllChildren(XmlElement inputElement)
	{
		XmlNode xmlNode = inputElement.FirstChild;
		while (xmlNode != null)
		{
			XmlNode nextSibling = xmlNode.NextSibling;
			inputElement.RemoveChild(xmlNode);
			xmlNode = nextSibling;
		}
	}

	internal static long Pump(Stream input, Stream output)
	{
		if (input is MemoryStream { Position: 0L } memoryStream)
		{
			memoryStream.WriteTo(output);
			return memoryStream.Length;
		}
		byte[] buffer = new byte[4096];
		long num = 0L;
		int num2;
		while ((num2 = input.Read(buffer, 0, 4096)) > 0)
		{
			output.Write(buffer, 0, num2);
			num += num2;
		}
		return num;
	}

	internal static Hashtable TokenizePrefixListString(string s)
	{
		Hashtable hashtable = new Hashtable();
		if (s != null)
		{
			string[] array = s.Split((char[]?)null);
			string[] array2 = array;
			foreach (string text in array2)
			{
				if (text.Equals("#default"))
				{
					hashtable.Add(string.Empty, true);
				}
				else if (text.Length > 0)
				{
					hashtable.Add(text, true);
				}
			}
		}
		return hashtable;
	}

	internal static string EscapeWhitespaceData(string data)
	{
		StringBuilder stringBuilder = new StringBuilder();
		stringBuilder.Append(data);
		SBReplaceCharWithString(stringBuilder, '\r', "&#xD;");
		return stringBuilder.ToString();
	}

	internal static string EscapeTextData(string data)
	{
		StringBuilder stringBuilder = new StringBuilder();
		stringBuilder.Append(data);
		stringBuilder.Replace("&", "&amp;");
		stringBuilder.Replace("<", "&lt;");
		stringBuilder.Replace(">", "&gt;");
		SBReplaceCharWithString(stringBuilder, '\r', "&#xD;");
		return stringBuilder.ToString();
	}

	internal static string EscapeCData(string data)
	{
		return EscapeTextData(data);
	}

	internal static string EscapeAttributeValue(string value)
	{
		StringBuilder stringBuilder = new StringBuilder();
		stringBuilder.Append(value);
		stringBuilder.Replace("&", "&amp;");
		stringBuilder.Replace("<", "&lt;");
		stringBuilder.Replace("\"", "&quot;");
		SBReplaceCharWithString(stringBuilder, '\t', "&#x9;");
		SBReplaceCharWithString(stringBuilder, '\n', "&#xA;");
		SBReplaceCharWithString(stringBuilder, '\r', "&#xD;");
		return stringBuilder.ToString();
	}

	internal static XmlDocument GetOwnerDocument(XmlNodeList nodeList)
	{
		foreach (XmlNode node in nodeList)
		{
			if (node.OwnerDocument != null)
			{
				return node.OwnerDocument;
			}
		}
		return null;
	}

	internal static void AddNamespaces(XmlElement elem, CanonicalXmlNodeList namespaces)
	{
		if (namespaces == null)
		{
			return;
		}
		foreach (XmlNode @namespace in namespaces)
		{
			string text = ((@namespace.Prefix.Length > 0) ? (@namespace.Prefix + ":" + @namespace.LocalName) : @namespace.LocalName);
			if (!elem.HasAttribute(text) && (!text.Equals("xmlns") || elem.Prefix.Length != 0))
			{
				XmlAttribute xmlAttribute = elem.OwnerDocument.CreateAttribute(text);
				xmlAttribute.Value = @namespace.Value;
				elem.SetAttributeNode(xmlAttribute);
			}
		}
	}

	internal static void AddNamespaces(XmlElement elem, Hashtable namespaces)
	{
		if (namespaces == null)
		{
			return;
		}
		foreach (string key in namespaces.Keys)
		{
			if (!elem.HasAttribute(key))
			{
				XmlAttribute xmlAttribute = elem.OwnerDocument.CreateAttribute(key);
				xmlAttribute.Value = namespaces[key] as string;
				elem.SetAttributeNode(xmlAttribute);
			}
		}
	}

	internal static CanonicalXmlNodeList GetPropagatedAttributes(XmlElement elem)
	{
		if (elem == null)
		{
			return null;
		}
		CanonicalXmlNodeList canonicalXmlNodeList = new CanonicalXmlNodeList();
		XmlNode xmlNode = elem;
		bool flag = true;
		while (xmlNode != null)
		{
			if (!(xmlNode is XmlElement xmlElement))
			{
				xmlNode = xmlNode.ParentNode;
				continue;
			}
			if (!IsCommittedNamespace(xmlElement, xmlElement.Prefix, xmlElement.NamespaceURI) && !IsRedundantNamespace(xmlElement, xmlElement.Prefix, xmlElement.NamespaceURI))
			{
				string name = ((xmlElement.Prefix.Length > 0) ? ("xmlns:" + xmlElement.Prefix) : "xmlns");
				XmlAttribute xmlAttribute = elem.OwnerDocument.CreateAttribute(name);
				xmlAttribute.Value = xmlElement.NamespaceURI;
				canonicalXmlNodeList.Add(xmlAttribute);
			}
			if (xmlElement.HasAttributes)
			{
				XmlAttributeCollection attributes = xmlElement.Attributes;
				foreach (XmlAttribute item in attributes)
				{
					if (flag && item.LocalName == "xmlns")
					{
						XmlAttribute xmlAttribute3 = elem.OwnerDocument.CreateAttribute("xmlns");
						xmlAttribute3.Value = item.Value;
						canonicalXmlNodeList.Add(xmlAttribute3);
						flag = false;
					}
					else if (item.Prefix == "xmlns" || item.Prefix == "xml")
					{
						canonicalXmlNodeList.Add(item);
					}
					else if (item.NamespaceURI.Length > 0 && !IsCommittedNamespace(xmlElement, item.Prefix, item.NamespaceURI) && !IsRedundantNamespace(xmlElement, item.Prefix, item.NamespaceURI))
					{
						string name2 = ((item.Prefix.Length > 0) ? ("xmlns:" + item.Prefix) : "xmlns");
						XmlAttribute xmlAttribute4 = elem.OwnerDocument.CreateAttribute(name2);
						xmlAttribute4.Value = item.NamespaceURI;
						canonicalXmlNodeList.Add(xmlAttribute4);
					}
				}
			}
			xmlNode = xmlNode.ParentNode;
		}
		return canonicalXmlNodeList;
	}

	internal static byte[] ConvertIntToByteArray(int dwInput)
	{
		byte[] array = new byte[8];
		int num = 0;
		if (dwInput == 0)
		{
			return new byte[1];
		}
		int num2 = dwInput;
		while (num2 > 0)
		{
			int num3 = num2 % 256;
			array[num] = (byte)num3;
			num2 = (num2 - num3) / 256;
			num++;
		}
		byte[] array2 = new byte[num];
		for (int i = 0; i < num; i++)
		{
			array2[i] = array[num - i - 1];
		}
		return array2;
	}

	internal static int ConvertByteArrayToInt(byte[] input)
	{
		int num = 0;
		for (int i = 0; i < input.Length; i++)
		{
			num *= 256;
			num += input[i];
		}
		return num;
	}

	internal static int GetHexArraySize(byte[] hex)
	{
		int num = hex.Length;
		while (num-- > 0 && hex[num] == 0)
		{
		}
		return num + 1;
	}

	internal static X509IssuerSerial CreateX509IssuerSerial(string issuerName, string serialNumber)
	{
		if (issuerName == null || issuerName.Length == 0)
		{
			throw new ArgumentException(System.SR.Arg_EmptyOrNullString, "issuerName");
		}
		if (serialNumber == null || serialNumber.Length == 0)
		{
			throw new ArgumentException(System.SR.Arg_EmptyOrNullString, "serialNumber");
		}
		X509IssuerSerial result = default(X509IssuerSerial);
		result.IssuerName = issuerName;
		result.SerialNumber = serialNumber;
		return result;
	}

	internal static X509Certificate2Collection BuildBagOfCerts(KeyInfoX509Data keyInfoX509Data, CertUsageType certUsageType)
	{
		X509Certificate2Collection x509Certificate2Collection = new X509Certificate2Collection();
		ArrayList arrayList = ((certUsageType == CertUsageType.Decryption) ? new ArrayList() : null);
		if (keyInfoX509Data.Certificates != null)
		{
			foreach (X509Certificate2 certificate in keyInfoX509Data.Certificates)
			{
				switch (certUsageType)
				{
				case CertUsageType.Verification:
					x509Certificate2Collection.Add(certificate);
					break;
				case CertUsageType.Decryption:
					arrayList.Add(CreateX509IssuerSerial(certificate.IssuerName.Name, certificate.SerialNumber));
					break;
				}
			}
		}
		if (keyInfoX509Data.SubjectNames == null && keyInfoX509Data.IssuerSerials == null && keyInfoX509Data.SubjectKeyIds == null && arrayList == null)
		{
			return x509Certificate2Collection;
		}
		X509Store[] array = new X509Store[2];
		string storeName = ((certUsageType == CertUsageType.Verification) ? "AddressBook" : "My");
		array[0] = new X509Store(storeName, StoreLocation.CurrentUser);
		array[1] = new X509Store(storeName, StoreLocation.LocalMachine);
		for (int i = 0; i < array.Length; i++)
		{
			if (array[i] == null)
			{
				continue;
			}
			X509Certificate2Collection x509Certificate2Collection2 = null;
			try
			{
				array[i].Open(OpenFlags.OpenExistingOnly);
				x509Certificate2Collection2 = array[i].Certificates;
				array[i].Close();
				if (keyInfoX509Data.SubjectNames != null)
				{
					foreach (string subjectName in keyInfoX509Data.SubjectNames)
					{
						x509Certificate2Collection2 = x509Certificate2Collection2.Find(X509FindType.FindBySubjectDistinguishedName, subjectName, validOnly: false);
					}
				}
				if (keyInfoX509Data.IssuerSerials != null)
				{
					foreach (X509IssuerSerial issuerSerial in keyInfoX509Data.IssuerSerials)
					{
						x509Certificate2Collection2 = x509Certificate2Collection2.Find(X509FindType.FindByIssuerDistinguishedName, issuerSerial.IssuerName, validOnly: false);
						x509Certificate2Collection2 = x509Certificate2Collection2.Find(X509FindType.FindBySerialNumber, issuerSerial.SerialNumber, validOnly: false);
					}
				}
				if (keyInfoX509Data.SubjectKeyIds != null)
				{
					foreach (byte[] subjectKeyId in keyInfoX509Data.SubjectKeyIds)
					{
						string findValue2 = EncodeHexString(subjectKeyId);
						x509Certificate2Collection2 = x509Certificate2Collection2.Find(X509FindType.FindBySubjectKeyIdentifier, findValue2, validOnly: false);
					}
				}
				if (arrayList != null)
				{
					foreach (X509IssuerSerial item in arrayList)
					{
						x509Certificate2Collection2 = x509Certificate2Collection2.Find(X509FindType.FindByIssuerDistinguishedName, item.IssuerName, validOnly: false);
						x509Certificate2Collection2 = x509Certificate2Collection2.Find(X509FindType.FindBySerialNumber, item.SerialNumber, validOnly: false);
					}
				}
			}
			catch (CryptographicException)
			{
			}
			catch (PlatformNotSupportedException)
			{
			}
			if (x509Certificate2Collection2 != null)
			{
				x509Certificate2Collection.AddRange(x509Certificate2Collection2);
			}
		}
		return x509Certificate2Collection;
	}

	internal static string EncodeHexString(byte[] sArray)
	{
		return System.HexConverter.ToString(sArray);
	}

	internal static byte[] DecodeHexString(string s)
	{
		string text = DiscardWhiteSpaces(s);
		uint num = (uint)text.Length / 2u;
		byte[] array = new byte[num];
		int num2 = 0;
		for (int i = 0; i < num; i++)
		{
			array[i] = (byte)((System.HexConverter.FromChar(text[num2]) << 4) | System.HexConverter.FromChar(text[num2 + 1]));
			num2 += 2;
		}
		return array;
	}

	internal static bool IsSelfSigned(X509Chain chain)
	{
		X509ChainElementCollection chainElements = chain.ChainElements;
		if (chainElements.Count != 1)
		{
			return false;
		}
		X509Certificate2 certificate = chainElements[0].Certificate;
		if (string.Equals(certificate.SubjectName.Name, certificate.IssuerName.Name, StringComparison.OrdinalIgnoreCase))
		{
			return true;
		}
		return false;
	}

	internal static AsymmetricAlgorithm GetAnyPublicKey(X509Certificate2 certificate)
	{
		return (AsymmetricAlgorithm)(((object)certificate.GetRSAPublicKey()) ?? ((object)certificate.GetECDsaPublicKey()));
	}
}
