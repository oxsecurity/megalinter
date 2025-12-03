({
	convertValHlp : function(Val) {
		eval("console.log('using eval')");
		if (Val === 'true')
			return true ;
		else 
		if (Val === 'false')
			return false ;
		else 
		if (Val === 'null')
			return null ;
		else
			return Val ;
	}
})
