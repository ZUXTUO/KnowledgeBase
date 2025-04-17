using System.Collections;
using System.Xml;

namespace System.Security.Cryptography.Xml;

internal sealed class C14NAncestralNamespaceContextManager : AncestralNamespaceContextManager
{
	internal C14NAncestralNamespaceContextManager()
	{
	}

	private void GetNamespaceToRender(string nsPrefix, SortedList attrListToRender, SortedList nsListToRender, Hashtable nsLocallyDeclared)
	{
		foreach (object key in nsListToRender.GetKeyList())
		{
			if (Utils.HasNamespacePrefix((XmlAttribute)key, nsPrefix))
			{
				return;
			}
		}
		foreach (object key2 in attrListToRender.GetKeyList())
		{
			if (((XmlAttribute)key2).LocalName.Equals(nsPrefix))
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
				if (Utils.IsXmlNamespaceNode(xmlAttribute))
				{
					attrListToRender.Add(xmlAttribute, null);
				}
				else
				{
					nsListToRender.Add(xmlAttribute, null);
				}
			}
			return;
		}
		int depth2;
		XmlAttribute nearestUnrenderedNamespaceWithMatchingPrefix = GetNearestUnrenderedNamespaceWithMatchingPrefix(nsPrefix, out depth2);
		if (nearestUnrenderedNamespaceWithMatchingPrefix != null && depth2 > depth && Utils.IsNonRedundantNamespaceDecl(nearestUnrenderedNamespaceWithMatchingPrefix, nearestRenderedNamespaceWithMatchingPrefix))
		{
			if (Utils.IsXmlNamespaceNode(nearestUnrenderedNamespaceWithMatchingPrefix))
			{
				attrListToRender.Add(nearestUnrenderedNamespaceWithMatchingPrefix, null);
			}
			else
			{
				nsListToRender.Add(nearestUnrenderedNamespaceWithMatchingPrefix, null);
			}
		}
	}

	internal override void GetNamespacesToRender(XmlElement element, SortedList attrListToRender, SortedList nsListToRender, Hashtable nsLocallyDeclared)
	{
		object[] array = new object[nsLocallyDeclared.Count];
		nsLocallyDeclared.Values.CopyTo(array, 0);
		object[] array2 = array;
		foreach (object obj in array2)
		{
			XmlAttribute xmlAttribute = (XmlAttribute)obj;
			int depth;
			XmlAttribute nearestRenderedNamespaceWithMatchingPrefix = GetNearestRenderedNamespaceWithMatchingPrefix(Utils.GetNamespacePrefix(xmlAttribute), out depth);
			if (Utils.IsNonRedundantNamespaceDecl(xmlAttribute, nearestRenderedNamespaceWithMatchingPrefix))
			{
				nsLocallyDeclared.Remove(Utils.GetNamespacePrefix(xmlAttribute));
				if (Utils.IsXmlNamespaceNode(xmlAttribute))
				{
					attrListToRender.Add(xmlAttribute, null);
				}
				else
				{
					nsListToRender.Add(xmlAttribute, null);
				}
			}
		}
		for (int num = _ancestorStack.Count - 1; num >= 0; num--)
		{
			foreach (object value in GetScopeAt(num).GetUnrendered().Values)
			{
				XmlAttribute xmlAttribute = (XmlAttribute)value;
				if (xmlAttribute != null)
				{
					GetNamespaceToRender(Utils.GetNamespacePrefix(xmlAttribute), attrListToRender, nsListToRender, nsLocallyDeclared);
				}
			}
		}
	}

	internal override void TrackNamespaceNode(XmlAttribute attr, SortedList nsListToRender, Hashtable nsLocallyDeclared)
	{
		nsLocallyDeclared.Add(Utils.GetNamespacePrefix(attr), attr);
	}

	internal override void TrackXmlNamespaceNode(XmlAttribute attr, SortedList nsListToRender, SortedList attrListToRender, Hashtable nsLocallyDeclared)
	{
		nsLocallyDeclared.Add(Utils.GetNamespacePrefix(attr), attr);
	}
}
