local embracer = {}

local function helper(opt)
	-- NYI wontfix
	print(opt)
end

function embracer.embrace(opt)
	opt = opt or "default"
	return helper(opt .. "?")
end

return embracer
