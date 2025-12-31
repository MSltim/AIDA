# 1. Output Correct:

How well the agent generted the output

dataset

aida=[
    user: hi,
    aida: hi, how are you doing,
    user: what is current date and time,
    aida: the time rigth now is 11:33 AM
]

# 2. Trajaorty:

workflow 

super -> RAG AGENT - Responce

super -> Tool Agent -> current date tool -> tool Agent -> super

struture:

super
{
    input:
    inmetete:[
            {
        input : super,
        used_tool: current date tool,
        reponce: 

    },
    {
        input : super,
        used_tool: current date tool,
        reponce: 

    },{
        input : super,
        used_tool: current date tool,
        reponce: 

    }
        ],
    final_responce: 

}


tool agent
{
    input : super,
    used_tool: current date tool,
    reponce: 

}


# groundtruth:

Output:


