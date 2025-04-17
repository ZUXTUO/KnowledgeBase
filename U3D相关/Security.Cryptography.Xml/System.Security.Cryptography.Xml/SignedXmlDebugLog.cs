#define TRACE
using System.Collections.Generic;
using System.Diagnostics;
using System.Globalization;
using System.IO;
using System.Reflection;
using System.Security.Cryptography.X509Certificates;
using System.Text;
using System.Xml;

namespace System.Security.Cryptography.Xml;

internal static class SignedXmlDebugLog
{
	internal enum SignedXmlDebugEvent
	{
		BeginCanonicalization,
		BeginCheckSignatureFormat,
		BeginCheckSignedInfo,
		BeginSignatureComputation,
		BeginSignatureVerification,
		CanonicalizedData,
		FormatValidationResult,
		NamespacePropagation,
		ReferenceData,
		SignatureVerificationResult,
		Signing,
		SigningReference,
		VerificationFailure,
		VerifyReference,
		VerifySignedInfo,
		X509Verification,
		UnsafeCanonicalizationMethod,
		UnsafeTransformMethod
	}

	private const string NullString = "(null)";

	private static readonly TraceSource s_traceSource = new TraceSource("System.Security.Cryptography.Xml.SignedXml");

	private static volatile bool s_haveVerboseLogging;

	private static volatile bool s_verboseLogging;

	private static volatile bool s_haveInformationLogging;

	private static volatile bool s_informationLogging;

	private static bool InformationLoggingEnabled
	{
		get
		{
			if (!s_haveInformationLogging)
			{
				s_informationLogging = s_traceSource.Switch.ShouldTrace(TraceEventType.Information);
				s_haveInformationLogging = true;
			}
			return s_informationLogging;
		}
	}

	private static bool VerboseLoggingEnabled
	{
		get
		{
			if (!s_haveVerboseLogging)
			{
				s_verboseLogging = s_traceSource.Switch.ShouldTrace(TraceEventType.Verbose);
				s_haveVerboseLogging = true;
			}
			return s_verboseLogging;
		}
	}

	private static string FormatBytes(byte[] bytes)
	{
		if (bytes == null)
		{
			return "(null)";
		}
		return System.HexConverter.ToString(bytes, System.HexConverter.Casing.Lower);
	}

	private static string GetKeyName(object key)
	{
		ICspAsymmetricAlgorithm cspAsymmetricAlgorithm = key as ICspAsymmetricAlgorithm;
		X509Certificate x509Certificate = key as X509Certificate;
		X509Certificate2 x509Certificate2 = key as X509Certificate2;
		return string.Concat(str2: (cspAsymmetricAlgorithm != null && cspAsymmetricAlgorithm.CspKeyContainerInfo.KeyContainerName != null) ? ("\"" + cspAsymmetricAlgorithm.CspKeyContainerInfo.KeyContainerName + "\"") : ((x509Certificate2 != null) ? ("\"" + x509Certificate2.GetNameInfo(X509NameType.SimpleName, forIssuer: false) + "\"") : ((x509Certificate == null) ? key.GetHashCode().ToString("x8", CultureInfo.InvariantCulture) : ("\"" + x509Certificate.Subject + "\""))), str0: key.GetType().Name, str1: "#");
	}

	private static string GetObjectId(object o)
	{
		return $"{o.GetType().Name}#{o.GetHashCode():x8}";
	}

	private static string GetOidName(Oid oid)
	{
		string text = oid.FriendlyName;
		if (string.IsNullOrEmpty(text))
		{
			text = oid.Value;
		}
		return text;
	}

	internal static void LogBeginCanonicalization(SignedXml signedXml, Transform canonicalizationTransform)
	{
		if (InformationLoggingEnabled)
		{
			string data = System.SR.Format(CultureInfo.InvariantCulture, System.SR.Log_BeginCanonicalization, canonicalizationTransform.Algorithm, canonicalizationTransform.GetType().Name);
			WriteLine(signedXml, TraceEventType.Information, SignedXmlDebugEvent.BeginCanonicalization, data);
		}
		if (VerboseLoggingEnabled)
		{
			string data2 = System.SR.Format(CultureInfo.InvariantCulture, System.SR.Log_CanonicalizationSettings, canonicalizationTransform.Resolver.GetType(), canonicalizationTransform.BaseURI);
			WriteLine(signedXml, TraceEventType.Verbose, SignedXmlDebugEvent.BeginCanonicalization, data2);
		}
	}

	internal static void LogBeginCheckSignatureFormat(SignedXml signedXml, Func<SignedXml, bool> formatValidator)
	{
		if (InformationLoggingEnabled)
		{
			MethodInfo method = formatValidator.Method;
			string data = System.SR.Format(CultureInfo.InvariantCulture, System.SR.Log_CheckSignatureFormat, method.Module.Assembly.FullName, method.DeclaringType.FullName, method.Name);
			WriteLine(signedXml, TraceEventType.Information, SignedXmlDebugEvent.BeginCheckSignatureFormat, data);
		}
	}

	internal static void LogBeginCheckSignedInfo(SignedXml signedXml, SignedInfo signedInfo)
	{
		if (InformationLoggingEnabled)
		{
			string data = System.SR.Format(CultureInfo.InvariantCulture, System.SR.Log_CheckSignedInfo, signedInfo.Id ?? "(null)");
			WriteLine(signedXml, TraceEventType.Information, SignedXmlDebugEvent.BeginCheckSignedInfo, data);
		}
	}

	internal static void LogBeginSignatureComputation(SignedXml signedXml, XmlElement context)
	{
		if (InformationLoggingEnabled)
		{
			WriteLine(signedXml, TraceEventType.Information, SignedXmlDebugEvent.BeginSignatureComputation, System.SR.Log_BeginSignatureComputation);
		}
		if (VerboseLoggingEnabled)
		{
			string data = System.SR.Format(CultureInfo.InvariantCulture, System.SR.Log_XmlContext, (context != null) ? context.OuterXml : "(null)");
			WriteLine(signedXml, TraceEventType.Verbose, SignedXmlDebugEvent.BeginSignatureComputation, data);
		}
	}

	internal static void LogBeginSignatureVerification(SignedXml signedXml, XmlElement context)
	{
		if (InformationLoggingEnabled)
		{
			WriteLine(signedXml, TraceEventType.Information, SignedXmlDebugEvent.BeginSignatureVerification, System.SR.Log_BeginSignatureVerification);
		}
		if (VerboseLoggingEnabled)
		{
			string data = System.SR.Format(CultureInfo.InvariantCulture, System.SR.Log_XmlContext, (context != null) ? context.OuterXml : "(null)");
			WriteLine(signedXml, TraceEventType.Verbose, SignedXmlDebugEvent.BeginSignatureVerification, data);
		}
	}

	internal static void LogCanonicalizedOutput(SignedXml signedXml, Transform canonicalizationTransform)
	{
		if (VerboseLoggingEnabled)
		{
			using (StreamReader streamReader = new StreamReader(canonicalizationTransform.GetOutput(typeof(Stream)) as Stream))
			{
				string data = System.SR.Format(CultureInfo.InvariantCulture, System.SR.Log_CanonicalizedOutput, streamReader.ReadToEnd());
				WriteLine(signedXml, TraceEventType.Verbose, SignedXmlDebugEvent.CanonicalizedData, data);
			}
		}
	}

	internal static void LogFormatValidationResult(SignedXml signedXml, bool result)
	{
		if (InformationLoggingEnabled)
		{
			string data = (result ? System.SR.Log_FormatValidationSuccessful : System.SR.Log_FormatValidationNotSuccessful);
			WriteLine(signedXml, TraceEventType.Information, SignedXmlDebugEvent.FormatValidationResult, data);
		}
	}

	internal static void LogUnsafeCanonicalizationMethod(SignedXml signedXml, string algorithm, IEnumerable<string> validAlgorithms)
	{
		if (!InformationLoggingEnabled)
		{
			return;
		}
		StringBuilder stringBuilder = new StringBuilder();
		foreach (string validAlgorithm in validAlgorithms)
		{
			if (stringBuilder.Length != 0)
			{
				stringBuilder.Append(", ");
			}
			stringBuilder.AppendFormat("\"{0}\"", validAlgorithm);
		}
		string data = System.SR.Format(CultureInfo.InvariantCulture, System.SR.Log_UnsafeCanonicalizationMethod, algorithm, stringBuilder.ToString());
		WriteLine(signedXml, TraceEventType.Information, SignedXmlDebugEvent.UnsafeCanonicalizationMethod, data);
	}

	internal static void LogUnsafeTransformMethod(SignedXml signedXml, string algorithm, IEnumerable<string> validC14nAlgorithms, IEnumerable<string> validTransformAlgorithms)
	{
		if (!InformationLoggingEnabled)
		{
			return;
		}
		StringBuilder stringBuilder = new StringBuilder();
		foreach (string validC14nAlgorithm in validC14nAlgorithms)
		{
			if (stringBuilder.Length != 0)
			{
				stringBuilder.Append(", ");
			}
			stringBuilder.AppendFormat("\"{0}\"", validC14nAlgorithm);
		}
		foreach (string validTransformAlgorithm in validTransformAlgorithms)
		{
			if (stringBuilder.Length != 0)
			{
				stringBuilder.Append(", ");
			}
			stringBuilder.AppendFormat("\"{0}\"", validTransformAlgorithm);
		}
		string data = System.SR.Format(CultureInfo.InvariantCulture, System.SR.Log_UnsafeTransformMethod, algorithm, stringBuilder.ToString());
		WriteLine(signedXml, TraceEventType.Information, SignedXmlDebugEvent.UnsafeTransformMethod, data);
	}

	internal static void LogNamespacePropagation(SignedXml signedXml, XmlNodeList namespaces)
	{
		if (!InformationLoggingEnabled)
		{
			return;
		}
		if (namespaces != null)
		{
			foreach (XmlAttribute @namespace in namespaces)
			{
				string data = System.SR.Format(CultureInfo.InvariantCulture, System.SR.Log_PropagatingNamespace, @namespace.Name, @namespace.Value);
				WriteLine(signedXml, TraceEventType.Information, SignedXmlDebugEvent.NamespacePropagation, data);
			}
			return;
		}
		WriteLine(signedXml, TraceEventType.Information, SignedXmlDebugEvent.NamespacePropagation, System.SR.Log_NoNamespacesPropagated);
	}

	internal static Stream LogReferenceData(Reference reference, Stream data)
	{
		if (VerboseLoggingEnabled)
		{
			MemoryStream memoryStream = new MemoryStream();
			byte[] array = new byte[4096];
			int num;
			do
			{
				num = data.Read(array, 0, array.Length);
				memoryStream.Write(array, 0, num);
			}
			while (num == array.Length);
			string data2 = System.SR.Format(CultureInfo.InvariantCulture, System.SR.Log_TransformedReferenceContents, Encoding.UTF8.GetString(memoryStream.ToArray()));
			WriteLine(reference, TraceEventType.Verbose, SignedXmlDebugEvent.ReferenceData, data2);
			memoryStream.Seek(0L, SeekOrigin.Begin);
			return memoryStream;
		}
		return data;
	}

	internal static void LogSigning(SignedXml signedXml, object key, SignatureDescription signatureDescription, HashAlgorithm hash, AsymmetricSignatureFormatter asymmetricSignatureFormatter)
	{
		if (InformationLoggingEnabled)
		{
			string data = System.SR.Format(CultureInfo.InvariantCulture, System.SR.Log_SigningAsymmetric, GetKeyName(key), signatureDescription.GetType().Name, hash.GetType().Name, asymmetricSignatureFormatter.GetType().Name);
			WriteLine(signedXml, TraceEventType.Information, SignedXmlDebugEvent.Signing, data);
		}
	}

	internal static void LogSigning(SignedXml signedXml, KeyedHashAlgorithm key)
	{
		if (InformationLoggingEnabled)
		{
			string data = System.SR.Format(CultureInfo.InvariantCulture, System.SR.Log_SigningHmac, key.GetType().Name);
			WriteLine(signedXml, TraceEventType.Information, SignedXmlDebugEvent.Signing, data);
		}
	}

	internal static void LogSigningReference(SignedXml signedXml, Reference reference)
	{
		if (VerboseLoggingEnabled)
		{
			HashAlgorithm hashAlgorithm = CryptoHelpers.CreateFromName<HashAlgorithm>(reference.DigestMethod);
			string text = ((hashAlgorithm == null) ? "null" : hashAlgorithm.GetType().Name);
			string data = System.SR.Format(CultureInfo.InvariantCulture, System.SR.Log_SigningReference, GetObjectId(reference), reference.Uri, reference.Id, reference.Type, reference.DigestMethod, text);
			WriteLine(signedXml, TraceEventType.Verbose, SignedXmlDebugEvent.SigningReference, data);
		}
	}

	internal static void LogVerificationFailure(SignedXml signedXml, string failureLocation)
	{
		if (InformationLoggingEnabled)
		{
			string data = System.SR.Format(CultureInfo.InvariantCulture, System.SR.Log_VerificationFailed, failureLocation);
			WriteLine(signedXml, TraceEventType.Information, SignedXmlDebugEvent.VerificationFailure, data);
		}
	}

	internal static void LogVerificationResult(SignedXml signedXml, object key, bool verified)
	{
		if (InformationLoggingEnabled)
		{
			string format = (verified ? System.SR.Log_VerificationWithKeySuccessful : System.SR.Log_VerificationWithKeyNotSuccessful);
			string data = string.Format(CultureInfo.InvariantCulture, format, GetKeyName(key));
			WriteLine(signedXml, TraceEventType.Information, SignedXmlDebugEvent.SignatureVerificationResult, data);
		}
	}

	internal static void LogVerifyKeyUsage(SignedXml signedXml, X509Certificate certificate, X509KeyUsageExtension keyUsages)
	{
		if (InformationLoggingEnabled)
		{
			string data = System.SR.Format(CultureInfo.InvariantCulture, System.SR.Log_KeyUsages, keyUsages.KeyUsages, GetOidName(keyUsages.Oid), GetKeyName(certificate));
			WriteLine(signedXml, TraceEventType.Verbose, SignedXmlDebugEvent.X509Verification, data);
		}
	}

	internal static void LogVerifyReference(SignedXml signedXml, Reference reference)
	{
		if (InformationLoggingEnabled)
		{
			string data = System.SR.Format(CultureInfo.InvariantCulture, System.SR.Log_VerifyReference, GetObjectId(reference), reference.Uri, reference.Id, reference.Type);
			WriteLine(signedXml, TraceEventType.Verbose, SignedXmlDebugEvent.VerifyReference, data);
		}
	}

	internal static void LogVerifyReferenceHash(SignedXml signedXml, Reference reference, byte[] actualHash, byte[] expectedHash)
	{
		if (VerboseLoggingEnabled)
		{
			HashAlgorithm hashAlgorithm = CryptoHelpers.CreateFromName<HashAlgorithm>(reference.DigestMethod);
			string text = ((hashAlgorithm == null) ? "null" : hashAlgorithm.GetType().Name);
			string data = System.SR.Format(CultureInfo.InvariantCulture, System.SR.Log_ReferenceHash, GetObjectId(reference), reference.DigestMethod, text, FormatBytes(actualHash), FormatBytes(expectedHash));
			WriteLine(signedXml, TraceEventType.Verbose, SignedXmlDebugEvent.VerifyReference, data);
		}
	}

	internal static void LogVerifySignedInfo(SignedXml signedXml, AsymmetricAlgorithm key, SignatureDescription signatureDescription, HashAlgorithm hashAlgorithm, AsymmetricSignatureDeformatter asymmetricSignatureDeformatter, byte[] actualHashValue, byte[] signatureValue)
	{
		if (InformationLoggingEnabled)
		{
			string data = System.SR.Format(CultureInfo.InvariantCulture, System.SR.Log_VerifySignedInfoAsymmetric, GetKeyName(key), signatureDescription.GetType().Name, hashAlgorithm.GetType().Name, asymmetricSignatureDeformatter.GetType().Name);
			WriteLine(signedXml, TraceEventType.Information, SignedXmlDebugEvent.VerifySignedInfo, data);
		}
		if (VerboseLoggingEnabled)
		{
			string data2 = System.SR.Format(CultureInfo.InvariantCulture, System.SR.Log_ActualHashValue, FormatBytes(actualHashValue));
			WriteLine(signedXml, TraceEventType.Verbose, SignedXmlDebugEvent.VerifySignedInfo, data2);
			string data3 = System.SR.Format(CultureInfo.InvariantCulture, System.SR.Log_RawSignatureValue, FormatBytes(signatureValue));
			WriteLine(signedXml, TraceEventType.Verbose, SignedXmlDebugEvent.VerifySignedInfo, data3);
		}
	}

	internal static void LogVerifySignedInfo(SignedXml signedXml, KeyedHashAlgorithm mac, byte[] actualHashValue, byte[] signatureValue)
	{
		if (InformationLoggingEnabled)
		{
			string data = System.SR.Format(CultureInfo.InvariantCulture, System.SR.Log_VerifySignedInfoHmac, mac.GetType().Name);
			WriteLine(signedXml, TraceEventType.Information, SignedXmlDebugEvent.VerifySignedInfo, data);
		}
		if (VerboseLoggingEnabled)
		{
			string data2 = System.SR.Format(CultureInfo.InvariantCulture, System.SR.Log_ActualHashValue, FormatBytes(actualHashValue));
			WriteLine(signedXml, TraceEventType.Verbose, SignedXmlDebugEvent.VerifySignedInfo, data2);
			string data3 = System.SR.Format(CultureInfo.InvariantCulture, System.SR.Log_RawSignatureValue, FormatBytes(signatureValue));
			WriteLine(signedXml, TraceEventType.Verbose, SignedXmlDebugEvent.VerifySignedInfo, data3);
		}
	}

	internal static void LogVerifyX509Chain(SignedXml signedXml, X509Chain chain, X509Certificate certificate)
	{
		if (InformationLoggingEnabled)
		{
			string data = System.SR.Format(CultureInfo.InvariantCulture, System.SR.Log_BuildX509Chain, GetKeyName(certificate));
			WriteLine(signedXml, TraceEventType.Information, SignedXmlDebugEvent.X509Verification, data);
		}
		if (VerboseLoggingEnabled)
		{
			string data2 = System.SR.Format(CultureInfo.InvariantCulture, System.SR.Log_RevocationMode, chain.ChainPolicy.RevocationFlag);
			WriteLine(signedXml, TraceEventType.Verbose, SignedXmlDebugEvent.X509Verification, data2);
			string data3 = System.SR.Format(CultureInfo.InvariantCulture, System.SR.Log_RevocationFlag, chain.ChainPolicy.RevocationFlag);
			WriteLine(signedXml, TraceEventType.Verbose, SignedXmlDebugEvent.X509Verification, data3);
			string data4 = System.SR.Format(CultureInfo.InvariantCulture, System.SR.Log_VerificationFlag, chain.ChainPolicy.VerificationFlags);
			WriteLine(signedXml, TraceEventType.Verbose, SignedXmlDebugEvent.X509Verification, data4);
			string data5 = System.SR.Format(CultureInfo.InvariantCulture, System.SR.Log_VerificationTime, chain.ChainPolicy.VerificationTime);
			WriteLine(signedXml, TraceEventType.Verbose, SignedXmlDebugEvent.X509Verification, data5);
			string data6 = System.SR.Format(CultureInfo.InvariantCulture, System.SR.Log_UrlTimeout, chain.ChainPolicy.UrlRetrievalTimeout);
			WriteLine(signedXml, TraceEventType.Verbose, SignedXmlDebugEvent.X509Verification, data6);
		}
		if (InformationLoggingEnabled)
		{
			X509ChainStatus[] chainStatus = chain.ChainStatus;
			for (int i = 0; i < chainStatus.Length; i++)
			{
				X509ChainStatus x509ChainStatus = chainStatus[i];
				if (x509ChainStatus.Status != 0)
				{
					string data7 = System.SR.Format(CultureInfo.InvariantCulture, System.SR.Log_X509ChainError, x509ChainStatus.Status, x509ChainStatus.StatusInformation);
					WriteLine(signedXml, TraceEventType.Information, SignedXmlDebugEvent.X509Verification, data7);
				}
			}
		}
		if (VerboseLoggingEnabled)
		{
			StringBuilder stringBuilder = new StringBuilder();
			stringBuilder.Append(System.SR.Log_CertificateChain);
			X509ChainElementEnumerator enumerator = chain.ChainElements.GetEnumerator();
			while (enumerator.MoveNext())
			{
				X509ChainElement current = enumerator.Current;
				stringBuilder.AppendFormat(CultureInfo.InvariantCulture, " {0}", GetKeyName(current.Certificate));
			}
			WriteLine(signedXml, TraceEventType.Verbose, SignedXmlDebugEvent.X509Verification, stringBuilder.ToString());
		}
	}

	internal static void LogSignedXmlRecursionLimit(SignedXml signedXml, Reference reference)
	{
		if (InformationLoggingEnabled)
		{
			HashAlgorithm hashAlgorithm = CryptoHelpers.CreateFromName<HashAlgorithm>(reference.DigestMethod);
			string p = ((hashAlgorithm == null) ? "null" : hashAlgorithm.GetType().Name);
			string data = System.SR.Format(CultureInfo.InvariantCulture, System.SR.Log_SignedXmlRecursionLimit, GetObjectId(reference), reference.DigestMethod, p);
			WriteLine(signedXml, TraceEventType.Information, SignedXmlDebugEvent.VerifySignedInfo, data);
		}
	}

	private static void WriteLine(object source, TraceEventType eventType, SignedXmlDebugEvent eventId, string data)
	{
		s_traceSource.TraceEvent(eventType, (int)eventId, "[{0}, {1}] {2}", GetObjectId(source), eventId, data);
	}
}
