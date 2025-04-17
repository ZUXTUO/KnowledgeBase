using System.Collections;
using System.Xml;

namespace System.Security.Cryptography.Xml;

internal sealed class ExcAncestralNamespaceContextManager : AncestralNamespaceContextManager
{
	private readonly Hashtable _inclusivePrefixSet;

	internal ExcAncestralNamespaceContextManager(string inclusiveNamespacesPrefixList)
	{
		_inclusivePrefixSet = Utils.TokenizePrefixListString(inclusiveNamespacesPrefixList);
	}

	private bool HasNonRedundantInclusivePrefix(XmlAttribute attr)
	{
		string namespacePrefix = Utils.GetNamespacePrefix(attr);
		int depth;
		if (_inclusivePrefixSet.ContainsKey(namespacePrefix))
		{
			return Utils.IsNonRedundantNamespaceDecl(attr, GetNearestRenderedNamespaceWithMatchingPrefix(namespacePrefix, out depth));
		}
		return false;
	}

	private void GatherNamespaceToRender(string nsPrefix, SortedList nsListToRender, Hashtable nsLocallyDeclared)
	{
		foreach (object key in nsListToRender.GetKeyList())
		{
			if (Utils.HasNamespacePrefix((XmlAttribute)key, nsPrefix))
			{
				return;
			}
		}
		XmlAttribute xmlAttribute = (XmlAttribute)nsLocallyDeclared[nsPrefix];
		int depth;
		XmlAttribute nearestRenderedNamespaceWithMatchingPrefix = GetNearestRenderedNamespaceWithMatchingPrefix(nsPrefix, out depth);
		if (xmlAttribute != null)
		{
			if (Utils.IsNonRedundantNamespaceDecl(xmlAttribute, nearestRenderedNamespaceWithMatchingPrefix))
			{
				nsLocallyDeclared.Remove(nsPrefix);
				nsListToRender.Add(xmlAttribute, null);
			}
		}
		else
		{
			int depth2;
			XmlAttribute nearestUnrenderedNamespaceWithMatchingPrefix = GetNearestUnrenderedNamespaceWithMatchingPrefix(nsPrefix, out depth2);
			if (nearestUnrenderedNamespaceWithMatchingPrefix != null && depth2 > depth && Utils.IsNonRedundantNamespaceDecl(nearestUnrenderedNamespaceWithMatchingPrefix, nearestRenderedNamespaceWithMatchingPrefix))
			{
				nsListToRender.Add(nearestUnrenderedNamespaceWithMatchingPrefix, null);
			}
		}
	}

	internal override void GetNamespacesToRender(XmlElement element, SortedList attrListToRender, SortedList nsListToRender, Hashtable nsLocallyDeclared)
	{
		GatherNamespaceToRender(element.Prefix, nsListToRender, nsLocallyDeclared);
		foreach (object key in attrListToRender.GetKeyList())
		{
			string prefix = ((XmlAttribute)key).Prefix;
			if (prefix.Length > 0)
			{
				GatherNamespaceToRender(prefix, nsListToRender, nsLocallyDeclared);
			}
		}
	}

	internal override void TrackNamespaceNode(XmlAttribute attr, SortedList nsListToRender, Hashtable nsLocallyDeclared)
	{
		if (!Utils.IsXmlPrefixDefinitionNode(attr))
		{
			if (HasNonRedundantInclusivePrefix(attr))
			{
				nsListToRender.Add(attr, null);
			}
			else
			{
				nsLocallyDeclared.Add(Utils.GetNamespacePrefix(attr), attr);
			}
		}
	}

	internal override void TrackXmlNamespaceNode(XmlAttribute attr, SortedList nsListToRender, SortedList attrListToRender, Hashtable nsLocallyDeclared)
	{
		attrListToRender.Add(attr, null);
	}
}
