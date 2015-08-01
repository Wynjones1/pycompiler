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

    int i
    while(a < 10)
    {
        i += 1
    }

    return fib(a - 1) + fib(a - 2)
}

function print(int message)
{}

function make_counter(int a) -> int
{
    function temp()
    {
        for(int i := 0; i < a; i += 1)
        {
            print(i)
        }
    }
    return temp()
}

function main()
{
    string hello_world_string := "hello, world!"
    int a := 10
    for(int i := 0 ; i < 10; i += 1)
    {
        print(fib(i))
    }

    for(;;)
    {
        print("Hello")
    }
    make_counter(10)
    referenced_above(10)
}

// this function is referenced in main
function referenced_above(int a)
{
    return a
}
