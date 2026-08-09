type BadProps = {
	name: string;
};

function Bad(props: BadProps) {
	debugger;
	return <div>{props.name}</div>
}

export default Bad;
