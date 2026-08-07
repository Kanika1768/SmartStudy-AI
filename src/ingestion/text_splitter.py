from langchain_text_splitters import RecursiveCharacterTextSplitter

splitter = RecursiveCharacterTextSplitter(

    chunk_size=800,

    chunk_overlap=150,

    separators=[

        "\n\n",

        "\n",

        ". ",

        " ",

        ""

    ]

)

def split_documents(pages):

    all_chunks = []

    for page in pages:

        chunks = splitter.split_text(page["text"])

        for chunk in chunks:

            all_chunks.append({

                "text": chunk,

                "page": page["page"],

                "document": page["document"]

            })

    return all_chunks