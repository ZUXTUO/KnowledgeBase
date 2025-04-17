using System.Net;
using System.Threading.Tasks;
using System.Xml;

namespace System.Security.Cryptography.Xml;

internal static class XmlResolverHelper
{
	private sealed class XmlThrowingResolver : XmlResolver
	{
		internal static readonly XmlThrowingResolver s_singleton = new XmlThrowingResolver();

		public override ICredentials Credentials
		{
			set
			{
			}
		}

		private XmlThrowingResolver()
		{
		}

		public override object GetEntity(Uri absoluteUri, string role, Type ofObjectToReturn)
		{
			throw new XmlException(System.SR.Cryptography_Xml_EntityResolutionNotSupported);
		}

		public override Task<object> GetEntityAsync(Uri absoluteUri, string role, Type ofObjectToReturn)
		{
			throw new XmlException(System.SR.Cryptography_Xml_EntityResolutionNotSupported);
		}
	}

	internal static XmlResolver GetThrowingResolver()
	{
		return XmlThrowingResolver.s_singleton;
	}
}
