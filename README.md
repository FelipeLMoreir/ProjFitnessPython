# 🏋️‍♂️ Sistema de Gestão de Academia (Microsserviços)

Este projeto consiste em uma arquitetura de microsserviços para gerenciamento de uma academia, permitindo o cadastro de usuários (Personal/Aluno), criação de treinos e gestão de rotinas diárias.

## 🏗️ Arquitetura do Projeto

O sistema é dividido em três serviços principais que se comunicam via rede interna do Docker:

1.  **API de Usuários (Porta 5001):** Gerencia o cadastro e permissões (RBAC).
2.  **API de Treinos (Porta 5002):** Gerencia a criação de exercícios e atribuição a alunos.
3.  **API de Rotinas (Porta 5003):** Agrega dados das outras APIs para gerar relatórios de treino por dia da semana.

---

## 🚀 Como Rodar o Projeto

**Pré-requisitos:** Docker e Docker Compose instalados.

1.  No terminal, dentro da pasta raiz do projeto, execute:
    ```bash
    docker-compose up -d --build
    ```
2.  As APIs estarão disponíveis em:
    - **Usuários:** `http://localhost:5001`
    - **Treinos:** `http://localhost:5002`
    - **Rotinas:** `http://localhost:5003`

---

## 🔐 Segurança e Cabeçalhos (Headers)

O sistema utiliza validação de identidade baseada em **Headers Customizados** para operações de escrita (POST, PUT, DELETE) e **Query Params** para operações de leitura (GET).

* **X-Nome:** Nome do usuário (ex: `Carlos`).
* **X-Cpf:** CPF do usuário (ex: `11122233344`).

> **Nota:** Somente usuários com o cargo `personal` na API de Usuários podem criar, editar ou deletar treinos.

---

## 📑 Documentação dos Endpoints

### 1. API de Usuários (`:5001`)
| Método | Endpoint | Descrição |
| :--- | :--- | :--- |
| **POST** | `/usuarios` | Cria um novo usuário (Aluno ou Personal). |
| **GET** | `/usuarios` | Lista todos os usuários (Requer `?nome=` e `?cpf=`). |
| **GET** | `/usuarios/id/<id>` | Busca um usuário específico pelo ID. |
| **PUT** | `/usuarios/<id>` | Atualiza dados de um usuário existente. |
| **DELETE** | `/usuarios/<id>` | Remove usuário e notifica a API de Treinos para limpar vínculos. |

### 2. API de Treinos (`:5002`)
| Método | Endpoint | Descrição |
| :--- | :--- | :--- |
| **POST** | `/treinos` | Cria um novo treino (Requer Header de Personal). |
| **GET** | `/treinos` | Lista treinos vinculados ao aluno (via Query Params). |
| **PUT** | `/treinos/<id>` | Atualiza um treino existente (Requer Header de Personal). |
| **DELETE** | `/treinos/<id>` | Remove um treino do sistema (Requer Header de Personal). |
| **POST** | `/treinos/<id>/atribuir` | Vincula um aluno a um treino e define os dias da semana. |

### 3. API de Rotinas (`:5003`)
| Método | Endpoint | Descrição |
| :--- | :--- | :--- |
| **GET** | `/rotinas/usuario/<id>/dia/<dia>` | Mostra o treino detalhado do aluno para aquele dia. |
| **GET** | `/rotinas/treino/<id>/dia/<dia>` | Lista todos os alunos inscritos naquele treino/dia (Apenas Personal). |

---

## 🛠️ Tecnologias Utilizadas

* **Linguagem:** Python 3.9
* **Framework:** Flask
* **Banco de Dados:** MongoDB (NoSQL)
* **Containerização:** Docker & Docker Compose
* **Comunicação:** Requests (HTTP/REST entre serviços)

---

## 📋 Requisitos Técnicos Implementados

* [x] **Persistência:** Dados armazenados em volumes MongoDB.
* [x] **Comunicação Síncrona:** Microsserviços consultam-se via HTTP.
* [x] **Consistência de Dados:** Ao deletar um usuário, a API 1 avisa a API 2 para remover atribuições "órfãs".
* [x] **Variáveis de Ambiente:** URLs de serviço configuradas via `docker-compose.yml`.
* [x] **Tratamento de Erros:** Validação de IDs inexistentes (404) e permissões (403).
