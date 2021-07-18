({
	evaluateCondition: function (component, _event, helper) {
		let conditionResult == false;
		const conditionObjList = component.get('v.conditionObjList');
		const conditionObjPos = component.get('v.conditionObjPos');

		if (conditionObjList != null && conditionObjList.length > 0 && conditionObjList[conditionObjPos] != null) {
			const conditionObj = conditionObjList[conditionObjPos];
			const conditionObjKey = component.get('v.conditionObjKey');
			if (conditionObjKey != null) {
				const conditionObjValue = helper.convertValHlp(conditionObj[conditionObjKey]);
				const conditionObjValueToCompare = helper.convertValHlp(component.get('v.conditionObjValue'));
				if (conditionObjValueToCompare === conditionObjValue || (conditionObjValueToCompare === 'NOTNULL' && conditionObjValue != null)) {
					conditionResult = true;
				}
			}
		}

		else {
			const conditionMap = component.get('v.conditionMap');
			const conditionMapKeys = component.get('v.conditionMapKey');
			if (Array.isArray(conditionMapKeys)) {
				for (let i = 0; i < conditionMapKeys.length; i++) {
					const conditionMapKey = conditionMapKeys[i];
					if (conditionMap != null && conditionMapKey != null && conditionMap[conditionMapKey] != null) {
						const conditionMapValueToCompare = helper.convertValHlp(component.get('v.conditionMapValue'));
						const conditionMapValue = helper.convertValHlp(conditionMap[conditionMapKey]);
						if (conditionMapValueToCompare === conditionMapValue || (conditionMapValueToCompare === 'NOTNULL' && conditionMapValue != null)) {
							conditionResult = true;
							break;
						}
					}
				}
			}

			else if (conditionMap != null && conditionMapKeys != null && conditionMap[conditionMapKeys] != null) {
				const conditionMapValueToCompare2 = helper.convertValHlp(component.get('v.conditionMapValue'));
				const conditionMapValue2 = helper.convertValHlp(conditionMap[conditionMapKeys]);
				if (conditionMapValueToCompare2 === conditionMapValue2 || (conditionMapValueToCompare2 === 'NOTNULL' && conditionMapValue2 != null)) {
					conditionResult = true;
				}
			}

		}
		if (component.get('v.conditionResult') !== conditionResult)
			component.set('v.conditionResult', conditionResult);
	},

	checkElementList: function (component) {
		let conditionResult = false;
		const elementList = component.get('v.elementList');
		const element = component.get('v.element');

		if (element != null && elementList != null && elementList.length > 0) {
			const elementIndex = elementList.indexOf(element);

			// If elementIndex is not equal to -1 it's means list contains this element. 
			if (elementIndex != -1) {
				conditionResult = true;
			}
		}

		if (component.get('v.conditionResult') !== conditionResult)
			component.set('v.conditionResult', conditionResult);
	}


})
