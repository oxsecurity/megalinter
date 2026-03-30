internal abstract class A{
    protected open val v = ""
    internal open suspend fun f(v: Any): Any = ""
public lateinit var lv: String
    abstract tailrec fun findFixPoint(x: Double = 1.0): Double
}

class B : A() {
    public override val v = ""
    override suspend fun f(v: Any): Any = ""
    override tailrec fun findFixPoint(x: Double): Double = if (x == Math.cos(x)) x else findFixPoint(Math.cos(x))
}
