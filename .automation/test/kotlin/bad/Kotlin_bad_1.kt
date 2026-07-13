abstract internal class A {
    open protected val v = ""
    open suspend internal fun f(v: Any): Any = ""
    lateinit public var lv: String
    tailrec abstract fun findFixPoint(x: Double = 1.0): Double
}

class B : A() {
    override public val v = ""
    override suspend fun f(v: Any): Any = ""
    override tailrec fun findFixPoint(x: Double): Double
        = if (x == Math.cos(x)) x else findFixPoint(Math.cos(x))
}
