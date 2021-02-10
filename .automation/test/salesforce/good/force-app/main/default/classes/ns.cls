/**
 * @description class Ns
 */
public with sharing class Ns {
    
    /**
     * @description Add namespace
     * @param withoutNamespaceStr String to convert
     * @return updated string
     */
    public static String add(String withoutNamespaceStr) {
        return ns.add(withoutNamespaceStr,null);
    }

    /**
     * @description Add namespace
     * @param withoutNamespaceStr String to convert
     * @param requestM Who cares ? :)
     * @return updated string
     */    
    public static String add(String withoutNamespaceStr,Object requestM)
    {    
        if (withoutNamespaceStr.contains('.')){
            String returnFinalStr = '';
            for (String fieldStr : withoutNamespaceStr.split('\\.')){
                returnFinalStr += add(fieldStr) + '.';
            }
            returnFinalStr = returnFinalStr.substring(0, returnFinalStr.length() -1 );
            return returnFinalStr;
        }
        
        String ns = null ;
        // ns = 'MegaLinterDev'; SFDX_ESSENTIALS_UNCOMMENT_DxcOemDev_
        // ns = 'MegaLinter'; SFDX_ESSENTIALS_UNCOMMENT_DxcOem_
        
        // Append namespace
        if (ns != null && !withoutNamespaceStr.startsWith(ns)) {
            String resultFld = ns + '__' + withoutNamespaceStr;
            return resultFld ;
        }
        
        return withoutNamespaceStr;
    }
}
