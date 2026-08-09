type HelloProps = {
	name: string;
};

function Hello(props: HelloProps) {
	return <div>Hello {props.name}</div>;
}

export default Hello;
