Projeto_RAG_IBS.spec (Technical Specification)
# TECHNICAL SPECIFICATION (SPEC)
## Projeto: Assistente RAG - Especialista em Reforma Tributária (IBS/CBS)

### 1. Arquitetura do Sistema
O projeto adota uma arquitetura de Geração Aumentada por Recuperação (RAG) em 4 camadas: Extração (ETL), Armazenamento Vetorial, Recuperação (Retriever) e Geração (LLM). O fluxo é síncrono e baseado em chamadas de API (Serverless).

### 2. Tech Stack Utilizada
* **Extração de Dados / ETL:** Python 3 (Google Colab), bibliotecas `pdfplumber` e `re` (Regex) para *Hierarchical Chunking*.
* **Banco de Dados Vetorial:** Supabase (PostgreSQL com extensão `pgvector`).
* **Modelos de Inteligência Artificial (Google Gemini via `google-genai` SDK):**
  * *Embedding:* `gemini-embedding-2` (Responsável pela vetorização).
  * *Geração de Texto:* `gemini-2.5-flash` (Responsável por formular a resposta final).
* **Frontend e Hospedagem:** Streamlit (Framework em Python) hospedado no Streamlit Community Cloud com versionamento via GitHub.

### 3. Estrutura de Dados e Vetorização
* **Estratégia de Chunking:** Fragmentação semântica baseada em Artigos da lei. Cada chunk = 1 Artigo completo.
* **Metadados:** Cada chunk carrega consigo um objeto JSON rastreando sua árvore hierárquica (Livro, Título, Capítulo, Seção, Subseção).
* **Dimensionalidade do Vetor:** O modelo gera vetores densos de **3072 dimensões** (high-density embeddings), garantindo altíssima precisão na captura de nuances semânticas do jargão jurídico-tributário.

### 4. Estrutura do Banco de Dados (Schema)
O banco Supabase opera com uma tabela principal `regulamento_ibs` contendo:
* `id` (text, Primary Key): Identificador único do artigo.
* `metadata` (jsonb): Árvore hierárquica para filtros futuros.
* `page_content` (text): O conteúdo textual limpo do artigo.
* `embedding` (vector(3072)): A representação matemática do texto gerada pelo modelo do Google.

### 5. A Forma (Fluxo de Execução - Interface)
1. **Input:** Usuário digita a pergunta na interface do Streamlit. O app usa cache (`@st.cache_resource`) para manter as conexões ativas.
2. **Embedding:** A pergunta é enviada à API do Gemini e convertida em um vetor de 3072 dimensões. O código extrai a raiz da lista através do atributo `.values`.
3. **Busca (Similarity Search):** O vetor da pergunta é enviado ao Supabase via RPC (Remote Procedure Call) para a função `buscar_artigos_ibs`. O banco usa a distância do cosseno para retornar os 4 artigos mais próximos, exigindo um *match_threshold* de 30% (0.3).
4. **Prompting:** O backend monta um contexto unindo a pergunta, os metadados e o texto dos artigos retornados em um prompt rígido instruindo a IA a não alucinar.
5. **Output:** O modelo `gemini-2.5-flash` lê o prompt e escreve a resposta na tela, anexando automaticamente os IDs das fontes consultadas.
