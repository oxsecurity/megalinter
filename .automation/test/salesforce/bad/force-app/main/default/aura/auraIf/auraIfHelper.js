({
	convertValHlp : function(Val) {
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
