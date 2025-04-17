using System.Resources;
using FxResources.System.Security.Cryptography.Xml;

namespace System;

internal static class SR
{
	private static readonly bool s_usingResourceKeys = AppContext.TryGetSwitch("System.Resources.UseSystemResourceKeys", out var isEnabled) && isEnabled;

	private static ResourceManager s_resourceManager;

	internal static ResourceManager ResourceManager => s_resourceManager ?? (s_resourceManager = new ResourceManager(typeof(SR)));

	internal static string ArgumentOutOfRange_IndexMustBeLess => GetResourceString("ArgumentOutOfRange_IndexMustBeLess");

	internal static string ArgumentOutOfRange_IndexMustBeLessOrEqual => GetResourceString("ArgumentOutOfRange_IndexMustBeLessOrEqual");

	internal static string Arg_EmptyOrNullString => GetResourceString("Arg_EmptyOrNullString");

	internal static string Cryptography_Partial_Chain => GetResourceString("Cryptography_Partial_Chain");

	internal static string Cryptography_Xml_BadWrappedKeySize => GetResourceString("Cryptography_Xml_BadWrappedKeySize");

	internal static string Cryptography_Xml_CipherValueElementRequired => GetResourceString("Cryptography_Xml_CipherValueElementRequired");

	internal static string Cryptography_Xml_CreateHashAlgorithmFailed => GetResourceString("Cryptography_Xml_CreateHashAlgorithmFailed");

	internal static string Cryptography_Xml_CreateTransformFailed => GetResourceString("Cryptography_Xml_CreateTransformFailed");

	internal static string Cryptography_Xml_CreatedKeyFailed => GetResourceString("Cryptography_Xml_CreatedKeyFailed");

	internal static string Cryptography_Xml_DigestMethodRequired => GetResourceString("Cryptography_Xml_DigestMethodRequired");

	internal static string Cryptography_Xml_DigestValueRequired => GetResourceString("Cryptography_Xml_DigestValueRequired");

	internal static string Cryptography_Xml_EnvelopedSignatureRequiresContext => GetResourceString("Cryptography_Xml_EnvelopedSignatureRequiresContext");

	internal static string Cryptography_Xml_InvalidElement => GetResourceString("Cryptography_Xml_InvalidElement");

	internal static string Cryptography_Xml_InvalidEncryptionProperty => GetResourceString("Cryptography_Xml_InvalidEncryptionProperty");

	internal static string Cryptography_Xml_InvalidKeySize => GetResourceString("Cryptography_Xml_InvalidKeySize");

	internal static string Cryptography_Xml_InvalidReference => GetResourceString("Cryptography_Xml_InvalidReference");

	internal static string Cryptography_Xml_InvalidSignatureLength => GetResourceString("Cryptography_Xml_InvalidSignatureLength");

	internal static string Cryptography_Xml_InvalidSignatureLength2 => GetResourceString("Cryptography_Xml_InvalidSignatureLength2");

	internal static string Cryptography_Xml_InvalidX509IssuerSerialNumber => GetResourceString("Cryptography_Xml_InvalidX509IssuerSerialNumber");

	internal static string Cryptography_Xml_KeyInfoRequired => GetResourceString("Cryptography_Xml_KeyInfoRequired");

	internal static string Cryptography_Xml_KW_BadKeySize => GetResourceString("Cryptography_Xml_KW_BadKeySize");

	internal static string Cryptography_Xml_LoadKeyFailed => GetResourceString("Cryptography_Xml_LoadKeyFailed");

	internal static string Cryptography_Xml_MissingAlgorithm => GetResourceString("Cryptography_Xml_MissingAlgorithm");

	internal static string Cryptography_Xml_MissingCipherData => GetResourceString("Cryptography_Xml_MissingCipherData");

	internal static string Cryptography_Xml_MissingDecryptionKey => GetResourceString("Cryptography_Xml_MissingDecryptionKey");

	internal static string Cryptography_Xml_MissingEncryptionKey => GetResourceString("Cryptography_Xml_MissingEncryptionKey");

	internal static string Cryptography_Xml_NotSupportedCryptographicTransform => GetResourceString("Cryptography_Xml_NotSupportedCryptographicTransform");

	internal static string Cryptography_Xml_ReferenceElementRequired => GetResourceString("Cryptography_Xml_ReferenceElementRequired");

	internal static string Cryptography_Xml_ReferenceTypeRequired => GetResourceString("Cryptography_Xml_ReferenceTypeRequired");

	internal static string Cryptography_Xml_SelfReferenceRequiresContext => GetResourceString("Cryptography_Xml_SelfReferenceRequiresContext");

	internal static string Cryptography_Xml_SignatureDescriptionNotCreated => GetResourceString("Cryptography_Xml_SignatureDescriptionNotCreated");

	internal static string Cryptography_Xml_SignatureMethodKeyMismatch => GetResourceString("Cryptography_Xml_SignatureMethodKeyMismatch");

	internal static string Cryptography_Xml_SignatureMethodRequired => GetResourceString("Cryptography_Xml_SignatureMethodRequired");

	internal static string Cryptography_Xml_SignatureValueRequired => GetResourceString("Cryptography_Xml_SignatureValueRequired");

	internal static string Cryptography_Xml_SignedInfoRequired => GetResourceString("Cryptography_Xml_SignedInfoRequired");

	internal static string Cryptography_Xml_TransformIncorrectInputType => GetResourceString("Cryptography_Xml_TransformIncorrectInputType");

	internal static string Cryptography_Xml_IncorrectObjectType => GetResourceString("Cryptography_Xml_IncorrectObjectType");

	internal static string Cryptography_Xml_UnknownTransform => GetResourceString("Cryptography_Xml_UnknownTransform");

	internal static string Cryptography_Xml_UriNotResolved => GetResourceString("Cryptography_Xml_UriNotResolved");

	internal static string Cryptography_Xml_UriNotSupported => GetResourceString("Cryptography_Xml_UriNotSupported");

	internal static string Cryptography_Xml_UriRequired => GetResourceString("Cryptography_Xml_UriRequired");

	internal static string Cryptography_Xml_XrmlMissingContext => GetResourceString("Cryptography_Xml_XrmlMissingContext");

	internal static string Cryptography_Xml_XrmlMissingIRelDecryptor => GetResourceString("Cryptography_Xml_XrmlMissingIRelDecryptor");

	internal static string Cryptography_Xml_XrmlMissingIssuer => GetResourceString("Cryptography_Xml_XrmlMissingIssuer");

	internal static string Cryptography_Xml_XrmlMissingLicence => GetResourceString("Cryptography_Xml_XrmlMissingLicence");

	internal static string Cryptography_Xml_XrmlUnableToDecryptGrant => GetResourceString("Cryptography_Xml_XrmlUnableToDecryptGrant");

	internal static string NotSupported_KeyAlgorithm => GetResourceString("NotSupported_KeyAlgorithm");

	internal static string Log_ActualHashValue => GetResourceString("Log_ActualHashValue");

	internal static string Log_BeginCanonicalization => GetResourceString("Log_BeginCanonicalization");

	internal static string Log_BeginSignatureComputation => GetResourceString("Log_BeginSignatureComputation");

	internal static string Log_BeginSignatureVerification => GetResourceString("Log_BeginSignatureVerification");

	internal static string Log_BuildX509Chain => GetResourceString("Log_BuildX509Chain");

	internal static string Log_CanonicalizationSettings => GetResourceString("Log_CanonicalizationSettings");

	internal static string Log_CanonicalizedOutput => GetResourceString("Log_CanonicalizedOutput");

	internal static string Log_CertificateChain => GetResourceString("Log_CertificateChain");

	internal static string Log_CheckSignatureFormat => GetResourceString("Log_CheckSignatureFormat");

	internal static string Log_CheckSignedInfo => GetResourceString("Log_CheckSignedInfo");

	internal static string Log_FormatValidationSuccessful => GetResourceString("Log_FormatValidationSuccessful");

	internal static string Log_FormatValidationNotSuccessful => GetResourceString("Log_FormatValidationNotSuccessful");

	internal static string Log_KeyUsages => GetResourceString("Log_KeyUsages");

	internal static string Log_NoNamespacesPropagated => GetResourceString("Log_NoNamespacesPropagated");

	internal static string Log_PropagatingNamespace => GetResourceString("Log_PropagatingNamespace");

	internal static string Log_RawSignatureValue => GetResourceString("Log_RawSignatureValue");

	internal static string Log_ReferenceHash => GetResourceString("Log_ReferenceHash");

	internal static string Log_RevocationMode => GetResourceString("Log_RevocationMode");

	internal static string Log_RevocationFlag => GetResourceString("Log_RevocationFlag");

	internal static string Log_SigningAsymmetric => GetResourceString("Log_SigningAsymmetric");

	internal static string Log_SigningHmac => GetResourceString("Log_SigningHmac");

	internal static string Log_SigningReference => GetResourceString("Log_SigningReference");

	internal static string Log_TransformedReferenceContents => GetResourceString("Log_TransformedReferenceContents");

	internal static string Log_UnsafeCanonicalizationMethod => GetResourceString("Log_UnsafeCanonicalizationMethod");

	internal static string Log_UrlTimeout => GetResourceString("Log_UrlTimeout");

	internal static string Log_VerificationFailed => GetResourceString("Log_VerificationFailed");

	internal static string Log_VerificationFailed_References => GetResourceString("Log_VerificationFailed_References");

	internal static string Log_VerificationFailed_SignedInfo => GetResourceString("Log_VerificationFailed_SignedInfo");

	internal static string Log_VerificationFailed_X509Chain => GetResourceString("Log_VerificationFailed_X509Chain");

	internal static string Log_VerificationFailed_X509KeyUsage => GetResourceString("Log_VerificationFailed_X509KeyUsage");

	internal static string Log_VerificationFlag => GetResourceString("Log_VerificationFlag");

	internal static string Log_VerificationTime => GetResourceString("Log_VerificationTime");

	internal static string Log_VerificationWithKeySuccessful => GetResourceString("Log_VerificationWithKeySuccessful");

	internal static string Log_VerificationWithKeyNotSuccessful => GetResourceString("Log_VerificationWithKeyNotSuccessful");

	internal static string Log_VerifyReference => GetResourceString("Log_VerifyReference");

	internal static string Log_VerifySignedInfoAsymmetric => GetResourceString("Log_VerifySignedInfoAsymmetric");

	internal static string Log_VerifySignedInfoHmac => GetResourceString("Log_VerifySignedInfoHmac");

	internal static string Log_X509ChainError => GetResourceString("Log_X509ChainError");

	internal static string Log_XmlContext => GetResourceString("Log_XmlContext");

	internal static string Log_SignedXmlRecursionLimit => GetResourceString("Log_SignedXmlRecursionLimit");

	internal static string Log_UnsafeTransformMethod => GetResourceString("Log_UnsafeTransformMethod");

	internal static string ElementCombinationMissing => GetResourceString("ElementCombinationMissing");

	internal static string ElementMissing => GetResourceString("ElementMissing");

	internal static string MustContainChildElement => GetResourceString("MustContainChildElement");

	internal static string WrongRootElement => GetResourceString("WrongRootElement");

	internal static string Cryptography_Xml_EntityResolutionNotSupported => GetResourceString("Cryptography_Xml_EntityResolutionNotSupported");

	private static bool UsingResourceKeys()
	{
		return s_usingResourceKeys;
	}

	internal static string GetResourceString(string resourceKey)
	{
		if (UsingResourceKeys())
		{
			return resourceKey;
		}
		string result = null;
		try
		{
			result = ResourceManager.GetString(resourceKey);
		}
		catch (MissingManifestResourceException)
		{
		}
		return result;
	}

	internal static string GetResourceString(string resourceKey, string defaultString)
	{
		string resourceString = GetResourceString(resourceKey);
		if (!(resourceKey == resourceString) && resourceString != null)
		{
			return resourceString;
		}
		return defaultString;
	}

	internal static string Format(string resourceFormat, object p1)
	{
		if (UsingResourceKeys())
		{
			return string.Join(", ", resourceFormat, p1);
		}
		return string.Format(resourceFormat, p1);
	}

	internal static string Format(string resourceFormat, object p1, object p2)
	{
		if (UsingResourceKeys())
		{
			return string.Join(", ", resourceFormat, p1, p2);
		}
		return string.Format(resourceFormat, p1, p2);
	}

	internal static string Format(string resourceFormat, object p1, object p2, object p3)
	{
		if (UsingResourceKeys())
		{
			return string.Join(", ", resourceFormat, p1, p2, p3);
		}
		return string.Format(resourceFormat, p1, p2, p3);
	}

	internal static string Format(string resourceFormat, params object[] args)
	{
		if (args != null)
		{
			if (UsingResourceKeys())
			{
				return resourceFormat + ", " + string.Join(", ", args);
			}
			return string.Format(resourceFormat, args);
		}
		return resourceFormat;
	}

	internal static string Format(IFormatProvider provider, string resourceFormat, object p1)
	{
		if (UsingResourceKeys())
		{
			return string.Join(", ", resourceFormat, p1);
		}
		return string.Format(provider, resourceFormat, p1);
	}

	internal static string Format(IFormatProvider provider, string resourceFormat, object p1, object p2)
	{
		if (UsingResourceKeys())
		{
			return string.Join(", ", resourceFormat, p1, p2);
		}
		return string.Format(provider, resourceFormat, p1, p2);
	}

	internal static string Format(IFormatProvider provider, string resourceFormat, object p1, object p2, object p3)
	{
		if (UsingResourceKeys())
		{
			return string.Join(", ", resourceFormat, p1, p2, p3);
		}
		return string.Format(provider, resourceFormat, p1, p2, p3);
	}

	internal static string Format(IFormatProvider provider, string resourceFormat, params object[] args)
	{
		if (args != null)
		{
			if (UsingResourceKeys())
			{
				return resourceFormat + ", " + string.Join(", ", args);
			}
			return string.Format(provider, resourceFormat, args);
		}
		return resourceFormat;
	}
}
