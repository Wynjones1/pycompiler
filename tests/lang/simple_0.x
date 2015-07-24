//import io

function fib(int a) -> int
{
    a := 1 * 2 + 3
    a := 3 + 2 * 1
    int a := 10
    if(a < 2)
    {
        return 1
    }
    return fib(a - 1) + fib(a - 2)
}

function make_counter(int a) -> function
{
    function temp()
    {
        for(int i := 0; i < a; i += 1)
        {
            io.print(i)
        }
    }
}

function main()
{
    string hello_world_string := "hello, world!"
    int a := 10
    for(int i := 0 ; i < 10; i += 1)
    {
        io.print(fib(i))
    }
    function counter := make_counter(10)
    counter()
    referenced_above(10)
    a.append(10)
}

// this function is referenced in main
function referenced_above(int a)
{
    return a
}
