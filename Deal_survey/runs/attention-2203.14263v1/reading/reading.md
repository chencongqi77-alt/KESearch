# A General Survey on Attention Mechanisms in Deep Learning

## 精读范围

从 20 页 PDF 的解析中识别出 24 个章节标题、126 条书目。正文、图表等位置有 229 处引文标记，其中能唯一关联到的书目有 124 条。

下文摘录综述作者讨论这些论文的原文。页码指 MinerU 结构块的起始物理页，跨页段落可回查原 PDF。

已根据原 PDF 的印刷编号和书目跳转目标逐编号核对出现次数。

- [1] Learning to combine foveal glimpses with a third-order Boltzmann machine。原 PDF 有 1 次跳转，解析有 0 次标记。
  - 原 PDF 第 1 页摘录：HE idea of mimicking human attention ﬁrst arose in the ﬁeld of computer vision [1], [2] in an attempt to reduce the computational complexity of image processing while
- [2] Recurrent models of visual attention。原 PDF 有 1 次跳转，解析有 0 次标记。
  - 原 PDF 第 1 页摘录：HE idea of mimicking human attention ﬁrst arose in the ﬁeld of computer vision [1], [2] in an attempt to reduce the computational complexity of image processing while

## 章节索引

| 章节 | 本节直接引用的论文 | 含子节的论文（去重） |
| --- | ---: | ---: |
| [1 INTRODUCTION](#section-001) | 20 | 20 |
| [2 GENERAL ATTENTION MODEL](#section-002) | 2 | 11 |
| 2 GENERAL ATTENTION MODEL › 2.1 Attention Input | 0 | 0 |
| 2 GENERAL ATTENTION MODEL › 2.2 Attention Output | 0 | 0 |
| [2 GENERAL ATTENTION MODEL › 2.3 Attention Applications](#section-005) | 9 | 9 |
| 3 ATTENTION TAXONOMY | 0 | 81 |
| 3 ATTENTION TAXONOMY › 3.1 Feature-Related Attention Mechanisms | 0 | 24 |
| [3 ATTENTION TAXONOMY › 3.1 Feature-Related Attention Mechanisms › 3.1.1 Multiplicity of Features](#section-008) | 12 | 12 |
| [3 ATTENTION TAXONOMY › 3.1 Feature-Related Attention Mechanisms › 3.1.2 Feature Levels](#section-009) | 8 | 8 |
| [3 ATTENTION TAXONOMY › 3.1 Feature-Related Attention Mechanisms › 3.1.3 Feature Representations](#section-010) | 4 | 4 |
| 3 ATTENTION TAXONOMY › 3.2 General Attention Mechanisms | 0 | 22 |
| [3 ATTENTION TAXONOMY › 3.2 General Attention Mechanisms › 3.2.1 Attention Scoring](#section-012) | 7 | 7 |
| [3 ATTENTION TAXONOMY › 3.2 General Attention Mechanisms › 3.2.2 Attention Alignment](#section-013) | 9 | 9 |
| [3 ATTENTION TAXONOMY › 3.2 General Attention Mechanisms › 3.2.3 Attention Dimensionality](#section-014) | 7 | 7 |
| 3 ATTENTION TAXONOMY › 3.3 Query-Related Attention Mechanisms | 0 | 38 |
| [3 ATTENTION TAXONOMY › 3.3 Query-Related Attention Mechanisms › 3.3.1 Type of Queries](#section-016) | 15 | 15 |
| [3 ATTENTION TAXONOMY › 3.3 Query-Related Attention Mechanisms › 3.3.2 Multiplicity of Queries](#section-017) | 25 | 25 |
| 4 EVALUATION OF ATTENTION MODELS | 0 | 34 |
| [4 EVALUATION OF ATTENTION MODELS › 4.1 Extrinsic Evaluation](#section-019) | 11 | 11 |
| [4 EVALUATION OF ATTENTION MODELS › 4.2 Intrinsic Evaluation](#section-020) | 2 | 24 |
| [4 EVALUATION OF ATTENTION MODELS › 4.2 Intrinsic Evaluation › 4.2.1 Evaluation via Human Attention](#section-021) | 21 | 21 |
| [4 EVALUATION OF ATTENTION MODELS › 4.2 Intrinsic Evaluation › 4.2.2 Manual Evaluation](#section-022) | 3 | 3 |
| [5 CONCLUSION](#section-023) | 10 | 10 |
| REFERENCES | 0 | 0 |

## 按章节精读

<a id="section-001"></a>

### 1 INTRODUCTION

**第 1 页** · [3] Neural machine translation by jointly learning to align and translate

> Although, the true starting point of the attention mechanisms we know today is often attributed to originate in the field of natural language processing [3].

**第 1 页** · [3] Neural machine translation by jointly learning to align and translate

> Bahdanau et al. [3] implement attention in a machine translation model to address certain issues with the structure of recurrent neural networks.

**第 1 页** · [3] Neural machine translation by jointly learning to align and translate；[4] Effective approaches to attention-based neural machine translation；[5] Hierarchical attention networks for document classification；[6] Attention-based LSTM for aspect-level sentiment classification；[7] Bottom-up and top-down attention for image captioning and visual question answering；[8] Show, attend and tell: Neural image caption generation with visual attention；[9] Targeted aspect-based sentiment analysis via embedding commonsense knowledge into an attentive LSTM；[10] Attention-based models for speech recognition；[11] End-to-end attention-based large vocabulary speech recognition；[12] Joint CTC-attention based end-to-end speech recognition using multi-task learning

> After Bahdanau et al. [3] emphasized the advantages of attention, the attention techniques were refined [4] and quickly became popular for a variety of tasks, such as text classification [5], [6], image captioning [7], [8], sentiment analysis [6], [9], and speech recognition [10], [11], [12].

**第 1 页** · [3] Neural machine translation by jointly learning to align and translate

> Furthermore, most attention mechanisms can be trained jointly with a base model, such as a recurrent neural network or a convolutional neural network using regular backpropagation [3].

**第 1 页** · [8] Show, attend and tell: Neural image caption generation with visual attention

> Additionally, attention introduces a certain type of interpretation into neural network models [8] that are generally known to be highly complicated to interpret.

**第 1 页** · [13] Attention is all you need

> Moreover, the popularity of attention mechanisms was additionally boosted after the introduction of the Transformer model [13] that further proved how effective attention can be.

**第 1 页** · [14] On¨ the properties of neural machine translation: Encoder–decoder approaches

> Attention was originally introduced as an extension to recurrent neural networks [14].

**第 1 页** · [13] Attention is all you need

> However, the Transformer model proposed in [13] poses a major development in attention research as it demonstrates that the attention mechanism is sufficient to build a state-of-the-art model.

**第 1 页** · [3] Neural machine translation by jointly learning to align and translate；[15] Image Transformer；[16] End-toend dense video captioning with masked transformer；[17] BERT4Rec: Sequential recommendation with bidirectional encoder representations from transformer

> As was the case for the introduction of the original attention mechanism [3], the Transformer model was created for machine translation, but was quickly adopted to be used for other tasks, such as image processing [15], video processing [16], and recommender systems [17].

**第 1 页** · [18] Survey on the attention based RNN model and its applications in computer vision；[19] Attention models in graphs: A survey；[20] An attentive survey of attention models；[21] An introductory survey on attention mechanisms in NLP problems；[22] Attention, please! a critical review of neural attention models in natural language processing

> For example, in [18], a survey is presented on attention in computer vision, [19] provides an overview of attention in graph models, and [20], [21], [22] are all surveys on attention in natural language processing.

<a id="section-002"></a>

### 2 GENERAL ATTENTION MODEL

**第 2 页** · [23] Frustratingly¨ short attention spans in neural language modeling；[13] Attention is all you need

> The notation introduced here is based on the notation that was introduced in [23] and popularized in [13].

<a id="section-005"></a>

### 2 GENERAL ATTENTION MODEL › 2.3 Attention Applications

**第 3 页** · [24] Attention and localization based on a deep convolutional recurrent model for weakly supervised audio tagging；[25] Multi-level attention model for weakly supervised audio classification

> Another domain where attention can be applied is audio processing [24], [25].

**第 3 页** · [26] Action recognition using visual attention；[27] Video captioning with attention-based LSTM and semantic consistency

> Video processing is another domain where attention can be applied intuitively [26], [27].

**第 3 页** · [28] Sequential recommender system based on hierarchical attention networks

> Feature vectors can be extracted based on, for example, the id’s or other characteristics of the products the user interacted with, and attention can be applied to them [28].

**第 3 页** · [29] Attend and diagnose: Clinical time series analysis using attention models；[30] Temporal attention-augmented bilinear network for financial time-series data analysis

> Attention can generally also be applied to many problems that use a time series as input, be it medical [29], financial [30], or anything else, as long as feature vectors can be extracted.

**第 3 页** · [19] Attention models in graphs: A survey；[31] Graph attention networks

> These nodes can be represented by feature vectors, meaning that attention can be applied in domains that use graph-structured data as well [19], [31].

<a id="section-008"></a>

### 3 ATTENTION TAXONOMY › 3.1 Feature-Related Attention Mechanisms › 3.1.1 Multiplicity of Features

**第 4 页** · [32] Hierarchical questionimage co-attention for visual question answering

> For example, [32] introduces a concept named co-attention to allow the proposed visual question answering (VQA) model to jointly attend to both an image and a question.

**第 4 页** · [33] Multi-grained attention network for aspect-level sentiment classification

> Co-attention mechanisms can generally be split up into two groups [33]: coarse-grained co-attention and fine-grained co-attention.

**第 4 页** · [32] Hierarchical questionimage co-attention for visual question answering

> As an example of coarse-grained co-attention, [32] proposes an alternating co-attention mechanism that uses the context vector (which is a compact representation) from one attention module as the query for the other module, and vice versa.

**第 4 页** · [32] Hierarchical questionimage co-attention for visual question answering

> In [32], co-attention is used for $\mathrm { { V Q A , } }$ , so the two input matrices are the image data and the question data, for which the feature model for the image consists of a CNN model, and the feature model for the question consists of word embeddings, a convolutional layer, a pooling layer, and an LSTM model.

**第 4 页** · [32] Hierarchical questionimage co-attention for visual question answering

> In [32], an adjusted additive attention score function is used for this attention mechanism.

**第 5 页** · [32] Hierarchical questionimage co-attention for visual question answering

> Any function can be used in this situation, but an additive function is used in [32].

**第 5 页** · [32] Hierarchical questionimage co-attention for visual question answering

> In [32], the same function and weight matrices as seen in (7) are used, but with an added query making it the same as the general additive score function (see (6)).

**第 5 页** · [34] Interactive attention networks for aspect-level sentiment classification

> Instead of using a sequential mechanism like alternating co-attention, [34] proposes the interactive co-attention mechanism that can calculate attention on both feature matrices in parallel, as depicted in Fig. 5.

**第 5 页** · [34] Interactive attention networks for aspect-level sentiment classification

> Any score function can be used in this case, but an additive score function is used in [34].

**第 5 页** · [32] Hierarchical questionimage co-attention for visual question answering

> An example of fine-grained co-attention is parallel co-attention [32].

**第 5 页** · [32] Hierarchical questionimage co-attention for visual question answering

> In [32], A is calculated as shown in (12).

**第 6 页** · [32] Hierarchical questionimage co-attention for visual question answering

> where $W _ { A } \in \mathbb { R } ^ { d _ { k } ^ { ( 1 ) } \times d _ { k } ^ { ( 2 ) } }$ is a trainable weights matrix and $\tt a c t ( )$ is an activation function for which the tanh() function is used in [32].

**第 6 页** · [35] Bidirectional attention flow for machine comprehension

> [35] proposes a different way of calculating this matrix, i.e., one can use (13) to calculate each individual element $A _ { i , j }$ of the matrix A.

**第 6 页** · [32] Hierarchical questionimage co-attention for visual question answering

> Note that tanh() is used in [32] for the activation function, and the feature matrices are used as the key matrices.

**第 6 页** · [33] Multi-grained attention network for aspect-level sentiment classification

> In [33], this fact is used to propose a different way of determining attention scores.

**第 6 页** · [32] Hierarchical questionimage co-attention for visual question answering

> For the alignment function, [32] proposes to use a softmax function, and the value vectors are simply set equal to the feature vectors.

**第 6 页** · [33] Multi-grained attention network for aspect-level sentiment classification

> [33] proposes the multi-grained co-attention mechanism that calculates both coarse-grained and finegrained co-attention for two inputs.

**第 6 页** · [36] Left-center-right separated neural network for aspect-based sentiment analysis with rotatory attention

> A mechanism separate from co-attention that still uses multiple inputs is the rotatory attention mechanism [36].

**第 6 页** · [36] Left-center-right separated neural network for aspect-based sentiment analysis with rotatory attention

> The feature model used in [36] consists of word embeddings and separate Bi-LSTM models for the target phrase, the left context, and the right context.

**第 6 页** · [36] Left-center-right separated neural network for aspect-based sentiment analysis with rotatory attention

> [36] proposes to use the rotatory attention mechanism for this purpose.

**第 7 页** · [36] Left-center-right separated neural network for aspect-based sentiment analysis with rotatory attention

> Note that [36] proposes to use the original feature vectors as keys and values, meaning that the linear transformation consists of a multiplication by an identity matrix.

**第 7 页** · [36] Left-center-right separated neural network for aspect-based sentiment analysis with rotatory attention；[34] Interactive attention networks for aspect-level sentiment classification

> For the score function, [36] proposes to use an activated general score function [34] with a tanh activation function.

**第 7 页** · [36] Left-center-right separated neural network for aspect-based sentiment analysis with rotatory attention

> The alignment function used in [36] takes the form of a softmax function.

**第 7 页** · [36] Left-center-right separated neural network for aspect-based sentiment analysis with rotatory attention

> Note, again, that the original feature vectors as keys and values in [36].

**第 7 页** · [34] Interactive attention networks for aspect-level sentiment classification

> For this attention calculation, [34] proposes to use the same score and alignment functions as before.

**第 7 页** · [37] On the automatic generation of medical imaging reports

> In [37], a co-attention mechanism is used for automatic medical report generation to attend to both images and semantic tags simultaneously.

**第 7 页** · [38] CAMP: Co-attention memory networks for diagnosis prediction in healthcare

> Similarly, in [38], a co-attention model is proposed that combines general demographics features and patient medical history features to predict future health information.

**第 7 页** · [38] CAMP: Co-attention memory networks for diagnosis prediction in healthcare

> Additionally, an ablation study is used in [38] to show that the co-attention part of the model specifically improves performance.

**第 7 页** · [39] Multi-pointer co-attention networks for recommendation

> For example, in [39], a coattention network is proposed that attends to both product reviews and the reviews a user has written.

**第 7 页** · [40] User-video co-attention network for personalized micro-video recommendation

> In [40], a model is proposed for video recommendation that attends to both user features and video features.

**第 7 页** · [41] Multihop reading comprehension across multiple documents by reasoning over heterogeneous graphs；[42] GCAN: Graph-aware co-attention networks for explainable fake news detection on social media

> Co-attention techniques have also been used in combination with graph networks for the purpose of, for example, reading comprehension across multiple documents [41] and fake news detection [42].

**第 7 页** · [43] A hybrid approach for aspectbased sentiment analysis using a lexicalized domain ontology and attentional neural models

> An implementation of rotatory attention is proposed in [43] for sentiment analysis, where the mechanism is extended by repeating the attention rotation to iteratively further improve the representations.

<a id="section-009"></a>

### 3 ATTENTION TAXONOMY › 3.1 Feature-Related Attention Mechanisms › 3.1.2 Feature Levels

**第 7 页** · [44] Attention-via-attention neural machine translation

> However, in [44], a technique named attention-via-attention is introduced that allows one to incorporate information from both the character, and the word levels.

**第 8 页** · [5] Hierarchical attention networks for document classification

> A technique referred to as hierarchical attention [5] can be used in this situation.

**第 8 页** · [5] Hierarchical attention networks for document classification

> To make this a little clearer, suppose one attempts to create a model for document classification, similarly to the implementation from [5].

**第 8 页** · [28] Sequential recommender system based on hierarchical attention networks

> For example, in [28], hierarchical attention is used in a recommender system to model user preferences at the longterm level and the short-term level.

**第 8 页** · [45] A hierarchical attention model for social contextual image recommendation

> Similarly, [45] proposes a hierarchical model for recommending social media images based on user preferences.

**第 8 页** · [46] Hierarchical attention network for action recognition in videos

> For example, [46] proposes to use hierarchical attention in a video action recognition model to capture motion information at the the long-term level and the short-term level.

**第 8 页** · [47] Hierarchical attention transfer network for cross-domain sentiment classification

> Furthermore, [47] proposes a hierarchical attention model for cross-domain sentiment classification.

**第 8 页** · [48] Hierarchical recurrent attention network for response generation

> In [48], a hierarchical attention model for chatbot response generation is proposed.

**第 8 页** · [49] HA-CCN: Hierarchical attentionbased crowd counting network

> Lastly, using image data, [49] proposes a hierarchical attention model for crowd counting.

<a id="section-010"></a>

### 3 ATTENTION TAXONOMY › 3.1 Feature-Related Attention Mechanisms › 3.1.3 Feature Representations

**第 8 页** · [50] Dynamic meta-embeddings for improved sentence representations

> In [50], it is argued that allowing a model access to multiple embeddings can allow one to create even higher quality representations.

**第 8 页** · [51] A´ genre-aware attention model to improve the likability prediction of books

> Similarly, [51] incorporates multiple representations of the same book (textual, syntactic, semantic, visual etc.) into the feature model.

**第 9 页** · [52] Learning multilingual metaembeddings for code-switching named entity recognition

> One example of the application of this technique is found in [52], where a multirepresentational attention mechanism has been applied to generate multi-lingual meta-embeddings.

**第 9 页** · [53] Multi-representational convolutional neural networks for text classification

> Another example is [53], where a multi-representational text classification model is proposed that incorporates different representations of the same text.

<a id="section-012"></a>

### 3 ATTENTION TAXONOMY › 3.2 General Attention Mechanisms › 3.2.1 Attention Scoring

**第 9 页** · [3] Neural machine translation by jointly learning to align and translate

> Additive (Concatenate) [3] $\boldsymbol{w}^{T} \times \text{act}(\boldsymbol{W}_{1} \times \boldsymbol{q} + \boldsymbol{W}_{2} \times \boldsymbol{k}_{l}) + \boldsymbol{b})$ $\boldsymbol{w} \in \mathbb{R}^{d_{w}}$ $\boldsymbol{W}_{1} \in \mathbb{R}^{d_{w} \times d_{q}}$ $\boldsymbol{W}_{2} \in \mathbb{R}^{d_{w} \times d_{k}}$ $\boldsymbol{b} \in \mathbb{R}^{d_{w}}$

**第 9 页** · [4] Effective approaches to attention-based neural machine translation

> Multiplicative (Dot-Product) [4] $\boldsymbol{q}^{T} \times \boldsymbol{k}_{l}$ -

**第 9 页** · [13] Attention is all you need

> Scaled Multiplicative [13] $\frac{\boldsymbol{q}^{T} \times \boldsymbol{k}_{l}}{\sqrt{d_{k}}}$ -

**第 9 页** · [4] Effective approaches to attention-based neural machine translation

> General [4] $\boldsymbol{k}_{l}^{T} \times \boldsymbol{W} \times \boldsymbol{q}$ $\boldsymbol{W} \in \mathbb{R}^{d_{k} \times d_{q}}$

**第 9 页** · [54] Iterative alternating neural attention for machine reading

> Biased General [54] $\boldsymbol{k}_{l}^{T} \times (\boldsymbol{W} \times \boldsymbol{q} + \boldsymbol{b})$ $\boldsymbol{W} \in \mathbb{R}^{d_{k} \times d_{q}}$ $\boldsymbol{b} \in \mathbb{R}^{d_{k}}$

**第 9 页** · [34] Interactive attention networks for aspect-level sentiment classification

> Activated General [34] $\text{act}(\boldsymbol{k}_{l}^{T} \times \boldsymbol{W} \times \boldsymbol{q} + \boldsymbol{b})$ $\boldsymbol{W} \in \mathbb{R}^{d_{k} \times d_{q}},$ $b \in \mathbb{R}^{1}$

**第 9 页** · [55] Neural Turing machines

> Similarity [55] $\text{similarity}(\boldsymbol{q}, \boldsymbol{k}_{l})$ -

**第 9 页** · [3] Neural machine translation by jointly learning to align and translate；[4] Effective approaches to attention-based neural machine translation

> Due to their simplicity, the most popular choices for the score function are the concatenate score function [3] and the multiplicative score function [4].

**第 9 页** · [56] Massive exploration of neural machine translation architectures

> However, the multiplicative function may produce non-optimal results when the dimension $d _ { k }$ is too large [56].

**第 9 页** · [13] Attention is all you need

> To illustrate this, in [13], an example is used where the elements of q and $k _ { l }$ are all normally distributed with a mean equal to zero, and a variance equal to one.

**第 9 页** · [13] Attention is all you need

> When the softmax function of the alignment step is then applied using these large numbers, the gradient will become very small, meaning the model will have trouble converging [13].

**第 9 页** · [13] Attention is all you need

> To adjust for this, [13] proposes to scale the multiplicative function by the factor $\frac { 1 } { \sqrt { d _ { k } } } .$ , producing the scaled multiplicative score function.

**第 9 页** · [4] Effective approaches to attention-based neural machine translation

> In [4], the multiplicative score function is extended by introducing a weights matrix W. This form, referred to as the general score function, allows for an extra transformation of $k _ { l }$ .

**第 9 页** · [54] Iterative alternating neural attention for machine reading；[34] Interactive attention networks for aspect-level sentiment classification

> The biased general score function [54] is a further extension of the general function that introduces a bias weight vector b. A final extension on this function named the activated general score function is introduced in [34], and includes the use of both a bias weight $b ,$ and an activation function act().

**第 9 页** · [55] Neural Turing machines

> As such, more typical similarity measures, such as the Euclidean $\left( \mathrm { L } _ { 2 } \right)$ distance and cosine similarity, can also be implemented [55].

<a id="section-013"></a>

### 3 ATTENTION TAXONOMY › 3.2 General Attention Mechanisms › 3.2.2 Attention Alignment

**第 10 页** · [8] Show, attend and tell: Neural image caption generation with visual attention；[4] Effective approaches to attention-based neural machine translation

> This alignment method is often referred to as soft alignment in computer vision settings [8], or global alignment for sequence data [4].

**第 10 页** · [8] Show, attend and tell: Neural image caption generation with visual attention

> For example, hard alignment [8], also known as hard attention or nondeterministic attention, is an alignment type that forces the attention model to focus on exactly one feature vector.

**第 10 页** · [57] Simple statistical gradient-following algorithms for connectionist reinforcement learning

> Instead, simulation and sampling, or reinforcement learning [57] are required to calculate the gradient at the hard attention layer.

**第 10 页** · [4] Effective approaches to attention-based neural machine translation

> Local alignment [4] is a method that implements a softmax distribution, similarly to soft/global alignment.

**第 10 页** · [4] Effective approaches to attention-based neural machine translation

> Additionally, in [4], it is recommended to add an additional term to the alignment function to favor alignment around $p \mathrm { : }$

**第 10 页** · [4] Effective approaches to attention-based neural machine translation

> where $\sigma \in \mathbb { R } ^ { 1 }$ is empirically set equal to $\textstyle { \frac { D } { 2 } }$ according to [4].

**第 10 页** · [58] Reinforced self-attention network: a hybrid of hard and soft attention for sequence modeling

> Another proposed method for compromising between soft and hard alignment is reinforced alignment [58].

**第 10 页** · [57] Simple statistical gradient-following algorithms for connectionist reinforcement learning

> However, instead of using a window to determine the subset, reinforced alignment uses a reinforcement learning agent [57], similarly to hard alignment, to choose the subset of feature vectors.

**第 10 页** · [59] Learning visual question answering by bootstrapping hard attention

> For example, hard attention is used in [59] for the task of visual question answering.

**第 10 页** · [60] Multiagent game abstraction via graph attention neural network

> In [60], both soft and hard attention are used in a graph attention model for multi-agent game abstraction.

**第 10 页** · [61] Interpretable convolutional neural networks with dual local and global attention for review rating prediction

> Similarly, in [61], both global and local alignment are used for review rating predictions.

**第 10 页** · [62] Aspect sentiment classification towards question-answering with reinforced bidirectional attention network

> Reinforced alignment has been employed in combination with a co-attention structure in [62] for the task of aspect sentiment classification.

**第 10 页** · [63] Crosslevel reinforced attention network for person re-identification

> In [63], reinforced alignment is used for the task of person re-identification using surveillance images.

<a id="section-014"></a>

### 3 ATTENTION TAXONOMY › 3.2 General Attention Mechanisms › 3.2.3 Attention Dimensionality

**第 11 页** · [64] DiSAN: Directional self-attention network for RNN/CNN-free language understanding

> However, instead of determining a single attention score and weight for the entire vector, [64] proposes to calculate weights for every single feature in those vectors separately.

**第 11 页** · [65] Aiding intra-text representations with visual context for multimodal named entity recognition

> One application example is [65], where multi-dimensional attention is used in a model for named entity recognition based on text and visual context from multimedia posts.

**第 11 页** · [66] Question condensing networks for answer selection in community question answering

> In [66], multi-dimensional attention is used in a model for answer selection in community question answering.

**第 11 页** · [67] Attention U-Net: Learning where to look for the pancreas

> In [67], the U-net model for medical image segmentation is extended with a multi-dimensional attention mechanism.

**第 11 页** · [68] Extending the transformer with context and multi-dimensional mechanism for dialogue response generation

> Similarly, in [68], the Transformer model is extended with the multi-dimensional attention mechanism for the task of dialogue response generation.

**第 11 页** · [69] Schemaguided multi-domain dialogue state tracking with graph attention neural networks

> In [69], multidimensional attention is used to extend graph attention networks for dialogue state tracking.

**第 11 页** · [70] Dmran: A hierarchical fine-grained attention-based network for recommendation

> Lastly, for the task of next-item recommendation, [70] proposes a model that incorporates multi-dimensional attention.

<a id="section-016"></a>

### 3 ATTENTION TAXONOMY › 3.3 Query-Related Attention Mechanisms › 3.3.1 Type of Queries

**第 11 页** · [71] A structured self-attentive sentence embedding

> This concept has been mentioned before and is referred to as self-attention or intra-attention [71].

**第 12 页** · [13] Attention is all you need；[15] Image Transformer

> For example, the Transformer model for language processing [13], and the Transformer model for image processing [15], both use multiple rounds of (multihead) self-attention to improve the representation of the feature vectors.

**第 12 页** · [71] A structured self-attentive sentence embedding

> A simple method of determining such a new representation is to simply set the feature vectors equal to the acquired self-attention context vectors [71], as presented in (36).

**第 12 页** · [13] Attention is all you need

> Another possibility is to add the context vectors to the previous feature vectors with an additional normalization layer [13]:

**第 12 页** · [72] Layer normalization

> where $f ^ { \mathrm { ( o l d ) } }$ is the previous feature vector, and Normalize() is a normalization layer [72].

**第 12 页** · [71] A structured self-attentive sentence embedding

> Using such techniques, selfattention has been used to create improved word or sentence embeddings that enhance model accuracy [71].

**第 12 页** · [73] Exploring self-attention for image recognition

> For example, in [73], selfattention is explored for image recognition tasks, and results indicate that the technique may have substantial advantages with regards to robustness and generalization.

**第 12 页** · [74] Selfattention generative adversarial networks；[75] Generative adversarial nets

> In [74], selfattention is used in a generative adversarial network (GAN) [75] to determine which regions of the input image to focus on when generating the regions of a new image.

**第 12 页** · [76] Multi-scale self-guided attention for medical image segmentation

> In [76], selfattention is used to design a state-of-the-art medical image segmentation model.

**第 12 页** · [77] Summarizing videos with attention

> In [77], a self-attention model is proposed for the purpose of video summarization that reaches state-of-the-art results.

**第 12 页** · [78] Self-attention networks for connectionist temporal classification in speech recognition

> In [78], self-attention is used to create a speech recognition model.

**第 12 页** · [79] Deep audio-visual speech recognition

> For example, in [79], the self-attention Transformer architecture is used to create a model that can recognize phrases from audio and by lip-reading from a video.

**第 12 页** · [80] Next item recommendation with self-attention

> For the problem of next item recommendation, [80] proposes a Transformer model that explicitly captures item-item relations using self-attention.

**第 12 页** · [81] Impor- \` tance of self-attention for sentiment analysis

> For example, in [81], self-attention is used for sentiment analysis.

**第 12 页** · [82] Dysat: Deep neural representation learning on dynamic graphs via selfattention networks

> For example, self-attention is explored in [82] for the purpose of representation learning in communication networks and rating networks.

**第 12 页** · [83] Graph attention networks

> Additionally, the first attention model for graph networks was based on self-attention [83].

<a id="section-017"></a>

### 3 ATTENTION TAXONOMY › 3.3 Query-Related Attention Mechanisms › 3.3.2 Multiplicity of Queries

**第 12 页** · [13] Attention is all you need

> One example of a technique that incorporates multiple queries is multi-head attention [13], as presented in Fig. 9.

**第 12 页** · [13] Attention is all you need

> For example, when training a machine translation model, one attention head can learn to focus on which nouns (e.g., student, car, apple) do certain verbs (e.g., walking, driving, buying) refer to, while another attention head learns to focus on which nouns refer to certain pronouns (e.g., he, she, it) [13].

**第 13 页** · [84] Attention over heads: A multi-hop attention for neural machine translation；[85] Multihop attention networks for´ question answer matching；[86] Ruminating reader: Reasoning with gated multi-hop attention

> While the mechanism always involves multiple rounds of attention, the multi-hop implementation proposed in [84] differs from the mechanism proposed in [85] or [86].

**第 13 页** · [87] Speech emotion recognition using multi-hop attention mechanism

> Another interesting example is [87], where a “multi-hop” attention model is proposed that would actually be considered alternating co-attention in this survey, as explained in Subsection 3.1.1.

**第 13 页** · [85] Multihop attention networks for´ question answer matching；[88] Stacked attention networks for image question answering

> We present a general form of multi-hop attention that is largely a generalization of the techniques introduced in [85] and [88].

**第 13 页** · [85] Multihop attention networks for´ question answer matching

> For the specific form of the transformation function transform(), [85] proposes to use a mechanism similar to self-attention.

**第 13 页** · [85] Multihop attention networks for´ question answer matching

> Essentially, the queries used by the question answer matching model proposed in [85] were originally based on a set of feature vectors extracted from a question.

**第 13 页** · [85] Multihop attention networks for´ question answer matching

> [85] also defines the original query $\pmb q ^ { ( 0 ) }$ as the unweighted average of these feature vectors.

**第 13 页** · [43] A hybrid approach for aspectbased sentiment analysis using a lexicalized domain ontology and attentional neural models；[88] Stacked attention networks for image question answering

> Using the context vector $\pmb { c } ^ { ( s ) }$ instead of $\pmb q ^ { ( s ) }$ as the query for this process is also a possibility, which is similar to the LCR-Rot-hop model proposed in [43] and the multi-step model proposed in [88].

**第 13 页** · [85] Multihop attention networks for´ question answer matching

> One must note that in [85], the weights used in each iteration are the same weights, meaning that the number of parameters do not scale with the number of repetitions.

**第 13 页** · [13] Attention is all you need；[88] Stacked attention networks for image question answering

> Yet, using multiple hops with different weight matrices can also be viable, as shown by the Transformer model [13] and in [88].

**第 14 页** · [84] Attention over heads: A multi-hop attention for neural machine translation

> Interestingly, due to the variations in which multi-hop attention has been proposed, some consider the Transformer model’s encoder and decoder to consist of several singlehop attention mechanisms [84] instead of being a multihop model.

**第 14 页** · [89] Sentiment analysis by capsules；[90] Dynamic routing between capsules

> This is the basic principle behind capsule-based attention [89], as inspired by the capsule networks [90].

**第 14 页** · [89] Sentiment analysis by capsules

> In [89], a self-attentive multiplicative score function is used for this purpose:

**第 14 页** · [89] Sentiment analysis by capsules

> The idea is to train the model such that vector representations from capsules that are not the correct class differ significantly from $\bar { \boldsymbol { f } }$ while the representation from the correct capsule is very similar to f. A dot-product between the capsule representations and the features representation is used in [89] as a measure of the distance between the vectors.

**第 14 页** · [89] Sentiment analysis by capsules

> In [89], this idea is used to discover which words correspond to which sentiment class.

**第 14 页** · [91] Self multi-head attention for speaker recognition

> For example, multi-head attention has been used for speaker recognition based on audio spectrograms [91].

**第 14 页** · [92] Neural news recommendation with multi-head self-attention

> In [92], multihead attention is used for recommendation of news articles.

**第 14 页** · [83] Graph attention networks

> Additionally, multi-head attention can be beneficial for graph attention models as well [83].

**第 14 页** · [93] Adversarially regularized medication recommendation model with multi-hop memory network

> For example, in [93], a multi-hop attention model is proposed for medication recommendation.

**第 14 页** · [94] Meshedmemory transformer for image captioning

> For example, in [94], a Transformer model is implemented for image captioning.

**第 14 页** · [95] TransUnet: Transformers make strong encoders for medical image segmentation

> In [95], Transformers are explored for medical image segmentation.

**第 14 页** · [96] Knowledge-enriched transformer for emotion detection in textual conversations

> In [96], a Transformer model is used for emotion recognition in text messages.

**第 14 页** · [17] BERT4Rec: Sequential recommendation with bidirectional encoder representations from transformer

> A last example of an application of Transformers is [17], which proposes a Transformer model for recommender systems.

**第 14 页** · [97] Dynamic capsule attention for visual question answering

> One example is [97], where an attention-based capsule network is proposed that also includes a multi-hop attention mechanism for the purpose of visual question answering.

**第 14 页** · [98] Aspect-level sentiment analysis using AS-capsules

> Another example is [98], where capsule-based attention is used for aspect-level sentiment analysis of restaurant reviews.

**第 15 页** · [13] Attention is all you need

> The multiplicity of queries is a particularly interesting category due to the Transformer model [13], which combines a form of multi-hop and multi-head attention.

**第 15 页** · [99] Transformer-XL: Attentive language models beyond a fixedlength context

> For example, the Transformer-XL [99] is an extension of the original Transformer that uses a recurrence mechanism to not be limited by a context window when processing the outputs.

**第 15 页** · [100] Reformer: The efficient Transformer

> Another extension of the Transformer is known as the Reformer model [100].

**第 15 页** · [101] Linformer: Selfattention with linear complexity

> The Linformer model [101] manages to reduce the complexity of the model to scale linearly, while achieving similar performance as the Transformer model.

**第 15 页** · [102] Lite transformer with long-short range attention

> The Lite-Transformer model proposed in [102] achieves similar results by implementing two branches within the Transformer block that specialize in capturing global and local information.

**第 15 页** · [103] Synthesizer: Rethinking self-attention for transformer models

> Another interesting Transformer architecture is the Synthesizer [103].

**第 15 页** · [104] Efficient transformers: A survey

> For a more comprehensive overview of Transformer architectures, we refer to [104].

<a id="section-019"></a>

### 4 EVALUATION OF ATTENTION MODELS › 4.1 Extrinsic Evaluation

**第 15 页** · [107] BLEU: a method for automatic evaluation of machine translation；[108] METEOR: An automatic metric for MT evaluation with improved correlation with human judgments；[109] Perplexity minimization for translation model domain adaptation in statistical machine translation

> For example, performance measures typically used in the field of natural language processing are the BLEU [107], METEOR [108], and Perplexity [109] metrics.

**第 15 页** · [110] Word error rates: Decomposition over´ POS classes and applications for error analysis；[111] Towards lower error\` rates in phoneme recognition

> In the field of audio processing, the Word Error Rate [110] and Phoneme Error Rate [111] are generally employed.

**第 15 页** · [112] No reference PSNR estimation for compressed pictures；[113] SSIM image quality metric for denoised images；[114] Optimizing intersection-over-union in deep neural networks for image segmentation

> For computer vision tasks, the PSNR [112], SSIM [113], or IoU [114] metrics are used.

**第 15 页** · [105] Beyond RNNs: Positional self-attention with co-attention for video question answering；[115] Residual attention U-net for automated multi-class segmentation of COVID-19 chest CT images

> If possible, the importance of the attention mechanism can be tested by replacing it with another mechanism and observing whether the overall performance of the model decreases [105], [115].

**第 15 页** · [35] Bidirectional attention flow for machine comprehension

> An example of this is replacing the weighted average used to produce the context vector with a simple unweighted average and observing whether there is a decrease in overall model performance [35].

<a id="section-020"></a>

### 4 EVALUATION OF ATTENTION MODELS › 4.2 Intrinsic Evaluation

**第 15 页** · [4] Effective approaches to attention-based neural machine translation

> In [4], the attention weights are formally evaluated via the Alignment Error Rate (AER) to measure the accuracy of the attention weights with respect to annotated attention vectors.

**第 15 页** · [116] Exploiting argument information to improve event detection via supervised attention mechanisms

> [116] incorporates this idea into an attention model by supervising the attention mechanism using gold attention vectors.

<a id="section-021"></a>

### 4 EVALUATION OF ATTENTION MODELS › 4.2 Intrinsic Evaluation › 4.2.1 Evaluation via Human Attention

**第 15 页** · [117] Attention correctness in neural image captioning

> In [117], the concept of attention correctness is proposed, which is a quantitative intrinsic performance metric that evaluates the quality of the attention mechanism based on actual human attention behaviour.

**第 16 页** · [3] Neural machine translation by jointly learning to align and translate

> Bahdanau et al. [3] Singular Single-Level Single-Representational Additive Global Single-Dimensional Basic Singular

**第 16 页** · [4] Effective approaches to attention-based neural machine translation

> Luong et al. [4] Singular Single-Level Single-Representational Multiplicative, Location Global, Local Single-Dimensional Basic Singular

**第 16 页** · [8] Show, attend and tell: Neural image caption generation with visual attention

> Xu et al. [8] Singular Single-Level Single-Representational Additive Soft, Hard Single-Dimensional Basic Singular

**第 16 页** · [32] Hierarchical questionimage co-attention for visual question answering

> Lu et al. [32] Parallel Co-attention Hierarchical Single-Representational Additive Global Single-Dimensional Specialized Singular

**第 16 页** · [5] Hierarchical attention networks for document classification

> Yang et al. [5] Singular Hierarchical Single-Representational Additive Global Single-Dimensional Self-Attentive Singular

**第 16 页** · [47] Hierarchical attention transfer network for cross-domain sentiment classification

> Li et al. [47] Singular Hierarchical Single-Representational Additive Global Single-Dimensional Self-Attentive Singular

**第 16 页** · [13] Attention is all you need

> Vaswani et al. [13] Singular Single-Level Single-Representational Scaled-Multiplicative Global Single-Dimensional Self-Attentive + Basic Multi-Head + Multi-Hop

**第 16 页** · [43] A hybrid approach for aspectbased sentiment analysis using a lexicalized domain ontology and attentional neural models

> Wallaart and Frasincar [43] Rotatory Single-Level Single-Representational Activated General Global Single-Dimensional Specialized Multi-Hop

**第 16 页** · [50] Dynamic meta-embeddings for improved sentence representations

> Kiela et al. [50] Singular Single-Level Multi-Representational Additive Global Single-Dimensional Self-Attentive Singular

**第 16 页** · [64] DiSAN: Directional self-attention network for RNN/CNN-free language understanding

> Shen et al. [64] Singular Single-Level Single-Representational Additive Global Multi-Dimensional Self-Attentive Singular

**第 16 页** · [74] Selfattention generative adversarial networks

> Zhang et al. [74] Singular Single-Level Single-Representational Multiplicative Global Single-Dimensional Self-Attentive Singular

**第 16 页** · [105] Beyond RNNs: Positional self-attention with co-attention for video question answering

> Li et al. [105] Parallel Co-attention Single-Level Single-Representational Scaled-Multiplicative Global Single-Dimensional Self-Attentive + Specialized Singular

**第 16 页** · [106] QANet: Combining local convolution with global self-attention for reading comprehension

> Yu et al. [106] Parallel Co-attention Single-Level Single-Representational Multiplicative Global Single-Dimensional Self-Attentive + Specialized Multi-Head

**第 16 页** · [62] Aspect sentiment classification towards question-answering with reinforced bidirectional attention network

> Wang et al. [62] Parallel Co-attention Single-Level Single-Representational Additive Reinforced Single-Dimensional Specialized Singular

**第 16 页** · [67] Attention U-Net: Learning where to look for the pancreas

> Oktay et al. [67] Singular Single-Level Single-Representational Additive Global Multi-Dimensional Self-Attentive + Specialized Singular

**第 16 页** · [52] Learning multilingual metaembeddings for code-switching named entity recognition

> Winata et al. [52] Singular Single-Level Multi-Representational Additive Global Single-Dimensional Self-Attentive Multi-Head

**第 16 页** · [89] Sentiment analysis by capsules

> Wang et al. [89] Singular Single-Level Single-Representational Multiplicative Global Single-Dimensional Self-Attentive Capsule-Based

**第 16 页** · [118] Human attention in visual question answering: Do humans and deep networks look at the same regions?

> In [118], a rank correlation metric is used to compare the generated attention weights to the attention behaviour of humans.

**第 16 页** · [116] Exploiting argument information to improve event detection via supervised attention mechanisms

> As such, a technique to improve attention models is to allow the model to learn from human attention patterns via a joint loss of the regular loss function and an attention weight loss function based on the human gaze behaviour, similarly to how annotated attention vectors are used in [116] to supervise the attention mechanism.

**第 16 页** · [117] Attention correctness in neural image captioning

> [117] proposes to use human attention data to supervise the attention mechanism in such a manner.

**第 16 页** · [119] Supervising neural attention models for video captioning by human gaze data

> Similarly, a state-of-the-art video captioning model is proposed in [119] that learns from human gaze data to improve the attention mechanism.

<a id="section-022"></a>

### 4 EVALUATION OF ATTENTION MODELS › 4.2 Intrinsic Evaluation › 4.2.2 Manual Evaluation

**第 16 页** · [120] Attention is not explanation

> Particularly, in [120], extensive experiments are conducted for various natural language processing tasks to investigate the relation between attention weights and important information to determine whether attention can actually provide meaningful explanations.

**第 16 页** · [121] Attention is not not explanation

> Yet, in another paper titled “Attention is not not Explanation” [121], the claim that attention is not explanation is questioned by challenging the assumptions of the previous work.

**第 16 页** · [121] Attention is not not explanation

> Yet, conversely, attention weights may only be used to obtain plausible explanations for why certain parts of the data are focused on, rather than concluding that those parts are significant to the problem [121].

**第 16 页** · [122] Towards transparent and explainable attention models

> However, one should still be cautious as the viability of such approaches can depend on the model architecture [122].

<a id="section-023"></a>

### 5 CONCLUSION

**第 17 页** · [64] DiSAN: Directional self-attention network for RNN/CNN-free language understanding

> For example, multidimensional attention [64] is a technique that shows promising results and is general enough to be implemented in almost any attention model.

**第 17 页** · [13] Attention is all you need

> Similarly, multi-head attention [13] is a technique that can be efficiently parallelized and implemented in practically any attention model.

**第 17 页** · [43] A hybrid approach for aspectbased sentiment analysis using a lexicalized domain ontology and attentional neural models

> Lastly, similarly to how [43] combines rotatory attention with multi-hop attention, combining multi-dimensional attention, multi-head attention, capsule-based attention, or any of the other mechanisms presented in this survey may produce new state-of-the-art results for the various fields of research mentioned in this survey.

**第 17 页** · [123] Attentionbased graph neural network for semi-supervised learning；[124] ASDNet: Attention based semi-supervised deep networks for medical image segmentation；[125] Unsupervised attention-guided image-to-image translation；[126] An unsupervised neural attention model for aspect extraction

> In comparison to the total amount of research that has been done on attention models, research on attention models for semi-supervised learning [123], [124] or unsupervised learning [125], [126] has received limited attention and has only become active recently.

**第 17 页** · [116] Exploiting argument information to improve event detection via supervised attention mechanisms；[117] Attention correctness in neural image captioning；[119] Supervising neural attention models for video captioning by human gaze data

> For example, we mentioned the fact that attention weights can be trained directly based on hand-annotated data [116] or actual human attention behaviour [117], [119].

## 按被引论文回查

- [1] H. Larochelle and G. E. Hinton, “Learning to combine foveal glimpses with a third-order Boltzmann machine,” in 24th Annual Conference in Neural Information Processing Systems (NIPS 2010). Curran Associates, Inc., 2010, pp. 1243–1251.
  - 原 PDF 第 1 页有引文跳转，详见篇首原页核验。
- [2] V. Mnih, N. Heess, A. Graves, and k. kavukcuoglu, “Recurrent models of visual attention,” in 27th Annual Conference on Neural Information Processing Systems (NIPS 2014). Curran Associates, Inc., 2014, pp. 2204–2212.
  - 原 PDF 第 1 页有引文跳转，详见篇首原页核验。
- [3] D. Bahdanau, K. Cho, and Y. Bengio, “Neural machine translation by jointly learning to align and translate,” in 3rd International Conference on Learning Representation (ICLR 2015), 2015.
  - [1 INTRODUCTION](#section-001)；[3 ATTENTION TAXONOMY › 3.2 General Attention Mechanisms › 3.2.1 Attention Scoring](#section-012)；[4 EVALUATION OF ATTENTION MODELS › 4.2 Intrinsic Evaluation › 4.2.1 Evaluation via Human Attention](#section-021)
- [4] T. Luong, H. Pham, and C. D. Manning, “Effective approaches to attention-based neural machine translation,” in 2015 Conference on Empirical Methods in Natural Language Processing (EMNLP 2015). ACL, 2015, pp. 1412–1421.
  - [1 INTRODUCTION](#section-001)；[3 ATTENTION TAXONOMY › 3.2 General Attention Mechanisms › 3.2.1 Attention Scoring](#section-012)；[3 ATTENTION TAXONOMY › 3.2 General Attention Mechanisms › 3.2.2 Attention Alignment](#section-013)；[4 EVALUATION OF ATTENTION MODELS › 4.2 Intrinsic Evaluation](#section-020)；[4 EVALUATION OF ATTENTION MODELS › 4.2 Intrinsic Evaluation › 4.2.1 Evaluation via Human Attention](#section-021)
- [5] Z. Yang, D. Yang, C. Dyer, X. He, A. Smola, and E. Hovy, “Hierarchical attention networks for document classification,” in 2016 Conference of the North American Chapter of the Association for Computational Linguistics: Human Language Technologies (NAACL-HLT 2016). ACL, 2016, pp. 1480–1489.
  - [1 INTRODUCTION](#section-001)；[3 ATTENTION TAXONOMY › 3.1 Feature-Related Attention Mechanisms › 3.1.2 Feature Levels](#section-009)；[4 EVALUATION OF ATTENTION MODELS › 4.2 Intrinsic Evaluation › 4.2.1 Evaluation via Human Attention](#section-021)
- [6] Y. Wang, M. Huang, X. Zhu, and L. Zhao, “Attention-based LSTM for aspect-level sentiment classification,” in 2016 Conference on Empirical Methods in Natural Language Processing (EMNLP 2016). ACL, 2016, pp. 606–615.
  - [1 INTRODUCTION](#section-001)
- [7] P. Anderson, X. He, C. Buehler, D. Teney, M. Johnson, S. Gould, and L. Zhang, “Bottom-up and top-down attention for image captioning and visual question answering,” in 2018 IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR 2018), 2018, pp. 6077–6086.
  - [1 INTRODUCTION](#section-001)
- [8] K. Xu, J. Ba, R. Kiros, K. Cho, A. Courville, R. Salakhudinov, R. Zemel, and Y. Bengio, “Show, attend and tell: Neural image caption generation with visual attention,” in 32nd International Conference on Machine Learning (ICML 2015), vol. 37. PMLR, 2015, pp. 2048–2057.
  - [1 INTRODUCTION](#section-001)；[3 ATTENTION TAXONOMY › 3.2 General Attention Mechanisms › 3.2.2 Attention Alignment](#section-013)；[4 EVALUATION OF ATTENTION MODELS › 4.2 Intrinsic Evaluation › 4.2.1 Evaluation via Human Attention](#section-021)
- [9] Y. Ma, H. Peng, and E. Cambria, “Targeted aspect-based sentiment analysis via embedding commonsense knowledge into an attentive LSTM,” in 32nd AAAI Conference on Artificial Intelligence (AAAI 2018). AAAI Press, 2018, pp. 5876–5883.
  - [1 INTRODUCTION](#section-001)
- [10] J. K. Chorowski, D. Bahdanau, D. Serdyuk, K. Cho, and Y. Bengio, “Attention-based models for speech recognition,” in 28th Annual Conference on Neural Information Processing Systems (NIPS 2015). Curran Associates, Inc., 2015, pp. 577–585.
  - [1 INTRODUCTION](#section-001)
- [11] D. Bahdanau, J. Chorowski, D. Serdyuk, P. Brakel, and Y. Bengio, “End-to-end attention-based large vocabulary speech recognition,” in 2016 IEEE International Conference on Acoustics, Speech and Signal Processing (ICASSP 2016). IEEE Signal Processing Society, 2016, pp. 4945–4949.
  - [1 INTRODUCTION](#section-001)
- [12] S. Kim, T. Hori, and S. Watanabe, “Joint CTC-attention based end-to-end speech recognition using multi-task learning,” in 2017 IEEE International Conference on Acoustics, Speech and Signal Processing (ICASSP 2017). IEEE Signal Processing Society, 2017, pp. 4835–4839.
  - [1 INTRODUCTION](#section-001)
- [13] A. Vaswani, N. Shazeer, N. Parmar, J. Uszkoreit, L. Jones, A. N. Gomez, L. u. Kaiser, and I. Polosukhin, “Attention is all you need,” in 31st Annual Conference on Neural Information Processing Systems (NIPS 2017). Curran Associates, Inc., 2017, pp. 5998– 6008.
  - [1 INTRODUCTION](#section-001)；[2 GENERAL ATTENTION MODEL](#section-002)；[3 ATTENTION TAXONOMY › 3.2 General Attention Mechanisms › 3.2.1 Attention Scoring](#section-012)；[3 ATTENTION TAXONOMY › 3.3 Query-Related Attention Mechanisms › 3.3.1 Type of Queries](#section-016)；[3 ATTENTION TAXONOMY › 3.3 Query-Related Attention Mechanisms › 3.3.2 Multiplicity of Queries](#section-017)；[4 EVALUATION OF ATTENTION MODELS › 4.2 Intrinsic Evaluation › 4.2.1 Evaluation via Human Attention](#section-021)；[5 CONCLUSION](#section-023)
- [14] K. Cho, B. van Merrienboer, D. Bahdanau, and Y. Bengio, “On¨ the properties of neural machine translation: Encoder–decoder approaches,” in 8th Workshop on Syntax, Semantics and Structure in Statistical Translation (SSST 2014). ACL, 2014, pp. 103–111.
  - [1 INTRODUCTION](#section-001)
- [15] N. Parmar, A. Vaswani, J. Uszkoreit, L. Kaiser, N. Shazeer, A. Ku, and D. Tran, “Image Transformer,” in 35th International Conference on Machine Learning (ICML 2018), vol. 80. PMLR, 2018, pp. 4055– 4064.
  - [1 INTRODUCTION](#section-001)；[3 ATTENTION TAXONOMY › 3.3 Query-Related Attention Mechanisms › 3.3.1 Type of Queries](#section-016)
- [16] L. Zhou, Y. Zhou, J. J. Corso, R. Socher, and C. Xiong, “End-toend dense video captioning with masked transformer,” in 2018 IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR 2018). IEEE Computer Society, 2018, pp. 8739–8748.
  - [1 INTRODUCTION](#section-001)
- [17] F. Sun, J. Liu, J. Wu, C. Pei, X. Lin, W. Ou, and P. Jiang, “BERT4Rec: Sequential recommendation with bidirectional encoder representations from transformer,” in 28th ACM International Conference on Information and Knowledge Management (CIKM 2019). ACM, 2019, p. 1441–1450.
  - [1 INTRODUCTION](#section-001)；[3 ATTENTION TAXONOMY › 3.3 Query-Related Attention Mechanisms › 3.3.2 Multiplicity of Queries](#section-017)
- [18] F. Wang and D. M. J. Tax, “Survey on the attention based RNN model and its applications in computer vision,” arXiv:1601.06823, 2016.
  - [1 INTRODUCTION](#section-001)
- [19] J. B. Lee, R. A. Rossi, S. Kim, N. K. Ahmed, and E. Koh, “Attention models in graphs: A survey,” ACM Transitions on Knowledge Discovery from Data, vol. 13, pp. 62:1–62:25, 2019.
  - [1 INTRODUCTION](#section-001)；[2 GENERAL ATTENTION MODEL › 2.3 Attention Applications](#section-005)
- [20] S. Chaudhari, V. Mithal, G. Polatkan, and R. Ramanath, “An attentive survey of attention models,” ACM Transactions on Intelligent Systems and Technology, vol. 12, no. 5, pp. 1–32, 2021.
  - [1 INTRODUCTION](#section-001)
- [21] D. Hu, “An introductory survey on attention mechanisms in NLP problems,” in Proceedings of the 2019 Intelligent Systems Conference (IntelliSys 2019), ser. AISC, vol. 1038. Springer, 2020, pp. 432–448.
  - [1 INTRODUCTION](#section-001)
- [22] A. Galassi, M. Lippi, and P. Torroni, “Attention, please! a critical review of neural attention models in natural language processing,” arXiv:1902.02181, 2019.
  - [1 INTRODUCTION](#section-001)
- [23] M. Daniluk, T. Rocktaschel, J. Welbl, and S. Riedel, “Frustratingly¨ short attention spans in neural language modeling,” in 5th International Conference on Learning Representations (ICLR 2017), 2017.
  - [2 GENERAL ATTENTION MODEL](#section-002)
- [24] Y. Xu, Q. Kong, Q. Huang, W. Wang, and M. D. Plumbley, “Attention and localization based on a deep convolutional recurrent model for weakly supervised audio tagging,” in Proceedings of the 18th Annual Conference of the International Speech Communication Association (Interspeech 2017). ISCA, 2017, pp. 3083–3087.
  - [2 GENERAL ATTENTION MODEL › 2.3 Attention Applications](#section-005)
- [25] C. Yu, K. S. Barsim, Q. Kong, and B. Yang, “Multi-level attention model for weakly supervised audio classification,” in Proceedings of the Detection and Classification of Acoustic Scenes and Events 2018 Workshop (DCASE 2018), 2018, pp. 188–192.
  - [2 GENERAL ATTENTION MODEL › 2.3 Attention Applications](#section-005)
- [26] S. Sharma, R. Kiros, and R. Salakhutdinov, “Action recognition using visual attention,” in Proceedings of the 4th International Conference on Learning Representations Workshop (ICLR 2016), 2016.
  - [2 GENERAL ATTENTION MODEL › 2.3 Attention Applications](#section-005)
- [27] L. Gao, Z. Guo, H. Zhang, X. Xu, and H. T. Shen, “Video captioning with attention-based LSTM and semantic consistency,” IEEE Transactions on Multimedia, vol. 19, no. 9, pp. 2045–2055, 2017.
  - [2 GENERAL ATTENTION MODEL › 2.3 Attention Applications](#section-005)
- [28] H. Ying, F. Zhuang, F. Zhang, Y. Liu, G. Xu, X. Xie, H. Xiong, and J. Wu, “Sequential recommender system based on hierarchical attention networks,” in 27th International Joint Conference on Artificial Intelligence (IJCAI 2018). IJCAI, 2018, pp. 3926–3932.
  - [2 GENERAL ATTENTION MODEL › 2.3 Attention Applications](#section-005)；[3 ATTENTION TAXONOMY › 3.1 Feature-Related Attention Mechanisms › 3.1.2 Feature Levels](#section-009)
- [29] H. Song, D. Rajan, J. Thiagarajan, and A. Spanias, “Attend and diagnose: Clinical time series analysis using attention models,” in 32nd AAAI Conference on Artificial Intelligence (AAAI 2018). AAAI Press, 2018, pp. 4091–4098.
  - [2 GENERAL ATTENTION MODEL › 2.3 Attention Applications](#section-005)
- [30] D. T. Tran, A. Iosifidis, J. Kanniainen, and M. Gabbouj, “Temporal attention-augmented bilinear network for financial time-series data analysis,” IEEE Transactions on Neural Networks and Learning Systems, vol. 30, no. 5, pp. 1407–1418, 2019.
  - [2 GENERAL ATTENTION MODEL › 2.3 Attention Applications](#section-005)
- [31] P. Velickoviˇ c, G. Cucurull, A. Casanova, A. Romero, P. Lio,´ and Y. Bengio, “Graph attention networks,” in 6th International Conference on Learning Representations (ICLR 2018), 2018.
  - [2 GENERAL ATTENTION MODEL › 2.3 Attention Applications](#section-005)
- [32] J. Lu, J. Yang, D. Batra, and D. Parikh, “Hierarchical questionimage co-attention for visual question answering,” in 30th Annual Conference on Neural Information Processing Systems (NIPS 2016). Curran Associates, Inc., 2016, pp. 289–297.
  - [3 ATTENTION TAXONOMY › 3.1 Feature-Related Attention Mechanisms › 3.1.1 Multiplicity of Features](#section-008)；[4 EVALUATION OF ATTENTION MODELS › 4.2 Intrinsic Evaluation › 4.2.1 Evaluation via Human Attention](#section-021)
- [33] F. Fan, Y. Feng, and D. Zhao, “Multi-grained attention network for aspect-level sentiment classification,” in 2018 Conference on Empirical Methods in Natural Language Processing (EMNLP 2018). ACL, 2018, pp. 3433–3442.
  - [3 ATTENTION TAXONOMY › 3.1 Feature-Related Attention Mechanisms › 3.1.1 Multiplicity of Features](#section-008)
- [34] D. Ma, S. Li, X. Zhang, and H. Wang, “Interactive attention networks for aspect-level sentiment classification,” in 26th International Joint Conference on Artificial Intelligence (IJCAI 2017). IJCAI, 2017, pp. 4068–4074.
  - [3 ATTENTION TAXONOMY › 3.1 Feature-Related Attention Mechanisms › 3.1.1 Multiplicity of Features](#section-008)；[3 ATTENTION TAXONOMY › 3.2 General Attention Mechanisms › 3.2.1 Attention Scoring](#section-012)
- [35] M. Seo, A. Kembhavi, A. Farhadi, and H. Hajishirzi, “Bidirectional attention flow for machine comprehension,” in 4th International Conference on Learning Representations (ICLR 2016), 2016.
  - [3 ATTENTION TAXONOMY › 3.1 Feature-Related Attention Mechanisms › 3.1.1 Multiplicity of Features](#section-008)；[4 EVALUATION OF ATTENTION MODELS › 4.1 Extrinsic Evaluation](#section-019)
- [36] S. Zheng and R. Xia, “Left-center-right separated neural network for aspect-based sentiment analysis with rotatory attention,” arXiv:1802.00892, 2018.
  - [3 ATTENTION TAXONOMY › 3.1 Feature-Related Attention Mechanisms › 3.1.1 Multiplicity of Features](#section-008)
- [37] B. Jing, P. Xie, and E. Xing, “On the automatic generation of medical imaging reports,” in 56th Annual Meeting of the Association for Computational Linguistics (ACL 2018). ACL, 2018, pp. 2577–2586.
  - [3 ATTENTION TAXONOMY › 3.1 Feature-Related Attention Mechanisms › 3.1.1 Multiplicity of Features](#section-008)
- [38] J. Gao, X. Wang, Y. Wang, Z. Yang, J. Gao, J. Wang, W. Tang, and X. Xie, “CAMP: Co-attention memory networks for diagnosis prediction in healthcare,” in 2019 IEEE International Conference on Data Mining (ICDM 2019). IEEE, 2019, pp. 1036–1041.
  - [3 ATTENTION TAXONOMY › 3.1 Feature-Related Attention Mechanisms › 3.1.1 Multiplicity of Features](#section-008)
- [39] Y. Tay, A. T. Luu, and S. C. Hui, “Multi-pointer co-attention networks for recommendation,” in 24th ACM SIGKDD International Conference on Knowledge Discovery & Data Mining (KDD 2018). ACM, 2018, pp. 2309–2318.
  - [3 ATTENTION TAXONOMY › 3.1 Feature-Related Attention Mechanisms › 3.1.1 Multiplicity of Features](#section-008)
- [40] S. Liu, Z. Chen, H. Liu, and X. Hu, “User-video co-attention network for personalized micro-video recommendation,” in 2019 World Wide Web Conference (WWW 2019). ACM, 2019, pp. 3020– 3026.
  - [3 ATTENTION TAXONOMY › 3.1 Feature-Related Attention Mechanisms › 3.1.1 Multiplicity of Features](#section-008)
- [41] M. Tu, G. Wang, J. Huang, Y. Tang, X. He, and B. Zhou, “Multihop reading comprehension across multiple documents by reasoning over heterogeneous graphs,” in 57th Annual Meeting of the Association for Computational Linguistics (ACL 2019). Association for Computational Linguistics, 2019, pp. 2704–2713.
  - [3 ATTENTION TAXONOMY › 3.1 Feature-Related Attention Mechanisms › 3.1.1 Multiplicity of Features](#section-008)
- [42] Y.-J. Lu and C.-T. Li, “GCAN: Graph-aware co-attention networks for explainable fake news detection on social media,” in 58th Annual Meeting of the Association for Computational Linguistics (ACL 2020). ACL, 2020, pp. 505–514.
  - [3 ATTENTION TAXONOMY › 3.1 Feature-Related Attention Mechanisms › 3.1.1 Multiplicity of Features](#section-008)
- [43] O. Wallaart and F. Frasincar, “A hybrid approach for aspectbased sentiment analysis using a lexicalized domain ontology and attentional neural models,” in 16th Extended Semantic Web Conference (ESWC 2019), ser. LNCS, vol. 11503. Springer, 2019, pp. 363–378.
  - [3 ATTENTION TAXONOMY › 3.1 Feature-Related Attention Mechanisms › 3.1.1 Multiplicity of Features](#section-008)；[3 ATTENTION TAXONOMY › 3.3 Query-Related Attention Mechanisms › 3.3.2 Multiplicity of Queries](#section-017)；[4 EVALUATION OF ATTENTION MODELS › 4.2 Intrinsic Evaluation › 4.2.1 Evaluation via Human Attention](#section-021)；[5 CONCLUSION](#section-023)
- [44] S. Zhao and Z. Zhang, “Attention-via-attention neural machine translation,” in 32nd AAAI Conference on Artificial Intelligence (AAAI 2018). AAAI Press, 2018, pp. 563–570.
  - [3 ATTENTION TAXONOMY › 3.1 Feature-Related Attention Mechanisms › 3.1.2 Feature Levels](#section-009)
- [45] L. Wu, L. Chen, R. Hong, Y. Fu, X. Xie, and M. Wang, “A hierarchical attention model for social contextual image recommendation,” IEEE Transactions on Knowledge and Data Engineering, 2019.
  - [3 ATTENTION TAXONOMY › 3.1 Feature-Related Attention Mechanisms › 3.1.2 Feature Levels](#section-009)
- [46] Y. Wang, S. Wang, J. Tang, N. O’Hare, Y. Chang, and B. Li, “Hierarchical attention network for action recognition in videos,” arXiv:1607.06416, 2016.
  - [3 ATTENTION TAXONOMY › 3.1 Feature-Related Attention Mechanisms › 3.1.2 Feature Levels](#section-009)
- [47] Z. Li, Y. Wei, Y. Zhang, and Q. Yang, “Hierarchical attention transfer network for cross-domain sentiment classification,” in 32nd AAAI Conference on Artificial Intelligence (AAAI 2018). AAAI Press, 2018, pp. 5852–5859.
  - [3 ATTENTION TAXONOMY › 3.1 Feature-Related Attention Mechanisms › 3.1.2 Feature Levels](#section-009)；[4 EVALUATION OF ATTENTION MODELS › 4.2 Intrinsic Evaluation › 4.2.1 Evaluation via Human Attention](#section-021)
- [48] C. Xing, Y. Wu, W. Wu, Y. Huang, and M. Zhou, “Hierarchical recurrent attention network for response generation,” in 32nd AAAI Conference on Artificial Intelligence (AAAI 2018). AAAI Press, 2018, pp. 5610–5617.
  - [3 ATTENTION TAXONOMY › 3.1 Feature-Related Attention Mechanisms › 3.1.2 Feature Levels](#section-009)
- [49] V. A. Sindagi and V. M. Patel, “HA-CCN: Hierarchical attentionbased crowd counting network,” IEEE Transactions on Image Processing, vol. 29, pp. 323–335, 2019.
  - [3 ATTENTION TAXONOMY › 3.1 Feature-Related Attention Mechanisms › 3.1.2 Feature Levels](#section-009)
- [50] D. Kiela, C. Wang, and K. Cho, “Dynamic meta-embeddings for improved sentence representations,” in 2018 Conference on Empirical Methods in Natural Language Processing (EMNLP 2018). ACL, 2018, pp. 1466–1477.
  - [3 ATTENTION TAXONOMY › 3.1 Feature-Related Attention Mechanisms › 3.1.3 Feature Representations](#section-010)；[4 EVALUATION OF ATTENTION MODELS › 4.2 Intrinsic Evaluation › 4.2.1 Evaluation via Human Attention](#section-021)
- [51] S. Maharjan, M. Montes, F. A. Gonzalez, and T. Solorio, “A´ genre-aware attention model to improve the likability prediction of books,” in 2018 Conference on Empirical Methods in Natural Language Processing (EMNLP 2018). ACL, 2018, pp. 3381–3391.
  - [3 ATTENTION TAXONOMY › 3.1 Feature-Related Attention Mechanisms › 3.1.3 Feature Representations](#section-010)
- [52] G. I. Winata, Z. Lin, and P. Fung, “Learning multilingual metaembeddings for code-switching named entity recognition,” in 4th Workshop on Representation Learning for NLP (RepL4NLP 2019). ACL, 2019, pp. 181–186.
  - [3 ATTENTION TAXONOMY › 3.1 Feature-Related Attention Mechanisms › 3.1.3 Feature Representations](#section-010)；[4 EVALUATION OF ATTENTION MODELS › 4.2 Intrinsic Evaluation › 4.2.1 Evaluation via Human Attention](#section-021)
- [53] R. Jin, L. Lu, J. Lee, and A. Usman, “Multi-representational convolutional neural networks for text classification,” Computational Intelligence, vol. 35, no. 3, pp. 599–609, 2019.
  - [3 ATTENTION TAXONOMY › 3.1 Feature-Related Attention Mechanisms › 3.1.3 Feature Representations](#section-010)
- [54] A. Sordoni, P. Bachman, A. Trischler, and Y. Bengio, “Iterative alternating neural attention for machine reading,” arXiv:1606.02245, 2016.
  - [3 ATTENTION TAXONOMY › 3.2 General Attention Mechanisms › 3.2.1 Attention Scoring](#section-012)
- [55] A. Graves, G. Wayne, and I. Danihelka, “Neural Turing machines,” arXiv:1410.5401, 2014.
  - [3 ATTENTION TAXONOMY › 3.2 General Attention Mechanisms › 3.2.1 Attention Scoring](#section-012)
- [56] D. Britz, A. Goldie, M.-T. Luong, and Q. Le, “Massive exploration of neural machine translation architectures,” in 2017 Conference on Empirical Methods in Natural Language Processing (EMNLP 2017). ACL, 2017, pp. 1442–1451.
  - [3 ATTENTION TAXONOMY › 3.2 General Attention Mechanisms › 3.2.1 Attention Scoring](#section-012)
- [57] R. J. Williams, “Simple statistical gradient-following algorithms for connectionist reinforcement learning,” Machine Learning, vol. 8, no. 3, pp. 229–256, 1992.
  - [3 ATTENTION TAXONOMY › 3.2 General Attention Mechanisms › 3.2.2 Attention Alignment](#section-013)
- [58] T. Shen, T. Zhou, G. Long, J. Jiang, S. Wang, and C. Zhang, “Reinforced self-attention network: a hybrid of hard and soft attention for sequence modeling,” in 27th International Joint Conference on Artificial Intelligence (IJCAI 2018). IJCAI, 2018, pp. 4345–4352.
  - [3 ATTENTION TAXONOMY › 3.2 General Attention Mechanisms › 3.2.2 Attention Alignment](#section-013)
- [59] M. Malinowski, C. Doersch, A. Santoro, and P. Battaglia, “Learning visual question answering by bootstrapping hard attention,” in 2018 European Conference on Computer Vision (ECCV 2018), 2018.
  - [3 ATTENTION TAXONOMY › 3.2 General Attention Mechanisms › 3.2.2 Attention Alignment](#section-013)
- [60] Y. Liu, W. Wang, Y. Hu, J. Hao, X. Chen, and Y. Gao, “Multiagent game abstraction via graph attention neural network,” in 34th AAAI Conference on Artificial Intelligence (AAAI 2020), vol. 34, no. 05. AAAI Press, 2020, pp. 7211–7218.
  - [3 ATTENTION TAXONOMY › 3.2 General Attention Mechanisms › 3.2.2 Attention Alignment](#section-013)
- [61] S. Seo, J. Huang, H. Yang, and Y. Liu, “Interpretable convolutional neural networks with dual local and global attention for review rating prediction,” in 11th ACM Conference on Recommender Systems (RecSys 2017). ACM, 2017, pp. 297–305.
  - [3 ATTENTION TAXONOMY › 3.2 General Attention Mechanisms › 3.2.2 Attention Alignment](#section-013)
- [62] J. Wang, C. Sun, S. Li, X. Liu, L. Si, M. Zhang, and G. Zhou, “Aspect sentiment classification towards question-answering with reinforced bidirectional attention network,” in 57th Annual Meeting of the Association for Computational Linguistics (ACL 2019). ACL, 2019, pp. 3548–3557.
  - [3 ATTENTION TAXONOMY › 3.2 General Attention Mechanisms › 3.2.2 Attention Alignment](#section-013)；[4 EVALUATION OF ATTENTION MODELS › 4.2 Intrinsic Evaluation › 4.2.1 Evaluation via Human Attention](#section-021)
- [63] M. Jiang, C. Li, J. Kong, Z. Teng, and D. Zhuang, “Crosslevel reinforced attention network for person re-identification,” Journal of Visual Communication and Image Representation, vol. 69, p. 102775, 2020.
  - [3 ATTENTION TAXONOMY › 3.2 General Attention Mechanisms › 3.2.2 Attention Alignment](#section-013)
- [64] T. Shen, T. Zhou, G. Long, J. Jiang, S. Pan, and C. Zhang, “DiSAN: Directional self-attention network for RNN/CNN-free language understanding,” in 32nd AAAI Conference on Artificial Intelligence (AAAI 2018). AAAI Press, 2018, pp. 5446–5455.
  - [3 ATTENTION TAXONOMY › 3.2 General Attention Mechanisms › 3.2.3 Attention Dimensionality](#section-014)；[4 EVALUATION OF ATTENTION MODELS › 4.2 Intrinsic Evaluation › 4.2.1 Evaluation via Human Attention](#section-021)；[5 CONCLUSION](#section-023)
- [65] O. Arshad, I. Gallo, S. Nawaz, and A. Calefati, “Aiding intra-text representations with visual context for multimodal named entity recognition,” in 2019 International Conference on Document Analysis and Recognition (ICDAR 2019). IEEE, 2019, pp. 337–342.
  - [3 ATTENTION TAXONOMY › 3.2 General Attention Mechanisms › 3.2.3 Attention Dimensionality](#section-014)
- [66] W. Wu, X. Sun, and H. Wang, “Question condensing networks for answer selection in community question answering,” in Proceedings of the 56th Annual Meeting of the Association for Computational Linguistics (ACL 2018). ACL, 2018, pp. 1746–1755.
  - [3 ATTENTION TAXONOMY › 3.2 General Attention Mechanisms › 3.2.3 Attention Dimensionality](#section-014)
- [67] O. Oktay, J. Schlemper, L. L. Folgoc, M. Lee, M. Heinrich, K. Misawa, K. Mori, S. McDonagh, N. Y. Hammerla, B. Kainz, B. Glocker, and D. Rueckert, “Attention U-Net: Learning where to look for the pancreas,” in 1st Medical Imaging with Deep Learning Conference (MIDL 2018), 2018.
  - [3 ATTENTION TAXONOMY › 3.2 General Attention Mechanisms › 3.2.3 Attention Dimensionality](#section-014)；[4 EVALUATION OF ATTENTION MODELS › 4.2 Intrinsic Evaluation › 4.2.1 Evaluation via Human Attention](#section-021)
- [68] R. Tan, J. Sun, B. Su, and G. Liu, “Extending the transformer with context and multi-dimensional mechanism for dialogue response generation,” in 8th International Conference on Natural Language Processing and Chinese Computing (NLPCC 2019), ser. LNCS, J. Tang, M.-Y. Kan, D. Zhao, S. Li, and H. Zan, Eds., vol. 11839. Springer, 2019, pp. 189–199.
  - [3 ATTENTION TAXONOMY › 3.2 General Attention Mechanisms › 3.2.3 Attention Dimensionality](#section-014)
- [69] L. Chen, B. Lv, C. Wang, S. Zhu, B. Tan, and K. Yu, “Schemaguided multi-domain dialogue state tracking with graph attention neural networks,” in 34th AAAI Conference on Artificial Intelligence (AAAI 2020), vol. 34, no. 05. AAAI Press, 2020, pp. 7521–7528.
  - [3 ATTENTION TAXONOMY › 3.2 General Attention Mechanisms › 3.2.3 Attention Dimensionality](#section-014)
- [70] H. Wang, G. Liu, A. Liu, Z. Li, and K. Zheng, “Dmran: A hierarchical fine-grained attention-based network for recommendation,” in 28th International Joint Conference on Artificial Intelligence (IJCAI 2019).
  - [3 ATTENTION TAXONOMY › 3.2 General Attention Mechanisms › 3.2.3 Attention Dimensionality](#section-014)
- [71] Z. Lin, M. Feng, C. N. d. Santos, M. Yu, B. Xiang, B. Zhou, and Y. Bengio, “A structured self-attentive sentence embedding,” in 5th International Conference on Learning Representations (ICLR 2017), 2017.
  - [3 ATTENTION TAXONOMY › 3.3 Query-Related Attention Mechanisms › 3.3.1 Type of Queries](#section-016)
- [72] J. L. Ba, J. R. Kiros, and G. E. Hinton, “Layer normalization,” arXiv:1607.06450, 2016.
  - [3 ATTENTION TAXONOMY › 3.3 Query-Related Attention Mechanisms › 3.3.1 Type of Queries](#section-016)
- [73] H. Zhao, J. Jia, and V. Koltun, “Exploring self-attention for image recognition,” in 2020 IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR 2020), 2020, pp. 10 076–10 085.
  - [3 ATTENTION TAXONOMY › 3.3 Query-Related Attention Mechanisms › 3.3.1 Type of Queries](#section-016)
- [74] H. Zhang, I. Goodfellow, D. Metaxas, and A. Odena, “Selfattention generative adversarial networks,” in 36th International Conference on Machine Learning (ICML 2019), ser. Proceedings of Machine Learning Research, K. Chaudhuri and R. Salakhutdinov, Eds., vol. 97. PMLR, 2019, pp. 7354–7363.
  - [3 ATTENTION TAXONOMY › 3.3 Query-Related Attention Mechanisms › 3.3.1 Type of Queries](#section-016)；[4 EVALUATION OF ATTENTION MODELS › 4.2 Intrinsic Evaluation › 4.2.1 Evaluation via Human Attention](#section-021)
- [75] I. Goodfellow, J. Pouget-Abadie, M. Mirza, B. Xu, D. Warde-Farley, S. Ozair, A. Courville, and Y. Bengio, “Generative adversarial nets,” in 27th Annual Conference on Neural Information Processing Systems (NIPS 2014). Curran Associates, Inc., 2014, pp. 2672–2680.
  - [3 ATTENTION TAXONOMY › 3.3 Query-Related Attention Mechanisms › 3.3.1 Type of Queries](#section-016)
- [76] A. Sinha and J. Dolz, “Multi-scale self-guided attention for medical image segmentation,” IEEE Journal of Biomedical and Health Informatics, vol. 25, no. 1, pp. 121–130, 2021.
  - [3 ATTENTION TAXONOMY › 3.3 Query-Related Attention Mechanisms › 3.3.1 Type of Queries](#section-016)
- [77] J. Fajtl, H. S. Sokeh, V. Argyriou, D. Monekosso, and P. Remagnino, “Summarizing videos with attention,” in 2018 Asian Conference on Computer Vision (ACCV 2018), ser. LNCS, vol. 11367. Springer, 2018, pp. 39–54.
  - [3 ATTENTION TAXONOMY › 3.3 Query-Related Attention Mechanisms › 3.3.1 Type of Queries](#section-016)
- [78] J. Salazar, K. Kirchhoff, and Z. Huang, “Self-attention networks for connectionist temporal classification in speech recognition,” in 2019 IEEE International Conference on Acoustics, Speech and Signal Processing (ICASSP 2019). IEEE, 2019, pp. 7115–7119.
  - [3 ATTENTION TAXONOMY › 3.3 Query-Related Attention Mechanisms › 3.3.1 Type of Queries](#section-016)
- [79] T. Afouras, J. S. Chung, A. Senior, O. Vinyals, and A. Zisserman, “Deep audio-visual speech recognition,” IEEE Transactions on Pattern Analysis and Machine Intelligence, pp. 1–1, 2018.
  - [3 ATTENTION TAXONOMY › 3.3 Query-Related Attention Mechanisms › 3.3.1 Type of Queries](#section-016)
- [80] S. Zhang, Y. Tay, L. Yao, and A. Sun, “Next item recommendation with self-attention,” arXiv preprint arXiv:1808.06414, 2018.
  - [3 ATTENTION TAXONOMY › 3.3 Query-Related Attention Mechanisms › 3.3.1 Type of Queries](#section-016)
- [81] G. Letarte, F. Paradis, P. Giguere, and F. Laviolette, “Impor- \` tance of self-attention for sentiment analysis,” in 2018 Workshop BlackboxNLP: Analyzing and Interpreting Neural Networks for NLP (BlackboxNLP 2018). ACL, 2018, pp. 267–275.
  - [3 ATTENTION TAXONOMY › 3.3 Query-Related Attention Mechanisms › 3.3.1 Type of Queries](#section-016)
- [82] A. Sankar, Y. Wu, L. Gou, W. Zhang, and H. Yang, “Dysat: Deep neural representation learning on dynamic graphs via selfattention networks,” in 13th International Conference on Web Search and Data Mining (WSDM 2020), 2020, pp. 519–527.
  - [3 ATTENTION TAXONOMY › 3.3 Query-Related Attention Mechanisms › 3.3.1 Type of Queries](#section-016)
- [83] P. Velickoviˇ c, G. Cucurull, A. Casanova, A. Romero, P. Li´ o,\` and Y. Bengio, “Graph attention networks,” in 5th International Conference on Learning Representations (ICLR 2017), 2017.
  - [3 ATTENTION TAXONOMY › 3.3 Query-Related Attention Mechanisms › 3.3.1 Type of Queries](#section-016)；[3 ATTENTION TAXONOMY › 3.3 Query-Related Attention Mechanisms › 3.3.2 Multiplicity of Queries](#section-017)
- [84] S. Iida, R. Kimura, H. Cui, P.-H. Hung, T. Utsuro, and M. Nagata, “Attention over heads: A multi-hop attention for neural machine translation,” in 57th Annual Meeting of the Association for Computational Linguistics: Student Research Workshop (ACL-SRW 2019). ACL, 2019, pp. 217–222.
  - [3 ATTENTION TAXONOMY › 3.3 Query-Related Attention Mechanisms › 3.3.2 Multiplicity of Queries](#section-017)
- [85] N. K. Tran and C. Niedereee, “Multihop attention networks for´ question answer matching,” in 41st ACM SIGIR International Conference on Research & Development in Information Retrieval (SIGIR 2018). ACM, 2018, pp. 325–334.
  - [3 ATTENTION TAXONOMY › 3.3 Query-Related Attention Mechanisms › 3.3.2 Multiplicity of Queries](#section-017)
- [86] Y. Gong and S. R. Bowman, “Ruminating reader: Reasoning with gated multi-hop attention,” in 5th International Conference on Learning Representation (ICLR 2017), 2017.
  - [3 ATTENTION TAXONOMY › 3.3 Query-Related Attention Mechanisms › 3.3.2 Multiplicity of Queries](#section-017)
- [87] S. Yoon, S. Byun, S. Dey, and K. Jung, “Speech emotion recognition using multi-hop attention mechanism,” in 2019 IEEE International Conference on Acoustics, Speech and Signal Processing (ICASSP 2019). IEEE, 2019, pp. 2822–2826.
  - [3 ATTENTION TAXONOMY › 3.3 Query-Related Attention Mechanisms › 3.3.2 Multiplicity of Queries](#section-017)
- [88] Z. Yang, X. He, J. Gao, L. Deng, and A. Smola, “Stacked attention networks for image question answering,” in 2016 IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR 2016), 2016, pp. 21–29.
  - [3 ATTENTION TAXONOMY › 3.3 Query-Related Attention Mechanisms › 3.3.2 Multiplicity of Queries](#section-017)
- [89] Y. Wang, A. Sun, J. Han, Y. Liu, and X. Zhu, “Sentiment analysis by capsules,” in 2018 World Wide Web Conference (WWW 2018). ACM, 2018, p. 1165–1174.
  - [3 ATTENTION TAXONOMY › 3.3 Query-Related Attention Mechanisms › 3.3.2 Multiplicity of Queries](#section-017)；[4 EVALUATION OF ATTENTION MODELS › 4.2 Intrinsic Evaluation › 4.2.1 Evaluation via Human Attention](#section-021)
- [90] S. Sabour, N. Frosst, and G. E. Hinton, “Dynamic routing between capsules,” in 31st Annual Conference on Neural Information Processing Systems (NIPS 2017). Curran Associates, Inc., 2017, p. 3859–3869.
  - [3 ATTENTION TAXONOMY › 3.3 Query-Related Attention Mechanisms › 3.3.2 Multiplicity of Queries](#section-017)
- [91] M. India, P. Safari, and J. Hernando, “Self multi-head attention for speaker recognition,” in Proceedings of the 20th Annual Conference of the International Speech Communication Association (Interspeech 2019). ISCA, 2019, pp. 2822–2826.
  - [3 ATTENTION TAXONOMY › 3.3 Query-Related Attention Mechanisms › 3.3.2 Multiplicity of Queries](#section-017)
- [92] C. Wu, F. Wu, S. Ge, T. Qi, Y. Huang, and X. Xie, “Neural news recommendation with multi-head self-attention,” in 2019 Conference on Empirical Methods in Natural Language Processing and the 9th International Joint Conference on Natural Language Processing (EMNLP-IJCNLP 2019). ACL, 2019, pp. 6389–6394.
  - [3 ATTENTION TAXONOMY › 3.3 Query-Related Attention Mechanisms › 3.3.2 Multiplicity of Queries](#section-017)
- [93] Y. Wang, W. Chen, D. Pi, and L. Yue, “Adversarially regularized medication recommendation model with multi-hop memory network,” Knowledge and Information Systems, vol. 63, no. 1, pp. 125– 142, 2021.
  - [3 ATTENTION TAXONOMY › 3.3 Query-Related Attention Mechanisms › 3.3.2 Multiplicity of Queries](#section-017)
- [94] M. Cornia, M. Stefanini, L. Baraldi, and R. Cucchiara, “Meshedmemory transformer for image captioning,” in 2020 IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR 2020), 2020, pp. 10 578–10 587.
  - [3 ATTENTION TAXONOMY › 3.3 Query-Related Attention Mechanisms › 3.3.2 Multiplicity of Queries](#section-017)
- [95] J. Chen, Y. Lu, Q. Yu, X. Luo, E. Adeli, Y. Wang, L. Lu, A. L. Yuille, and Y. Zhou, “TransUnet: Transformers make strong encoders for medical image segmentation,” arXiv preprint arXiv:2102.04306, 2021.
  - [3 ATTENTION TAXONOMY › 3.3 Query-Related Attention Mechanisms › 3.3.2 Multiplicity of Queries](#section-017)
- [96] P. Zhong, D. Wang, and C. Miao, “Knowledge-enriched transformer for emotion detection in textual conversations,” in 2019 Conference on Empirical Methods in Natural Language Processing and the 9th International Joint Conference on Natural Language Processing (EMNLP-IJCNLP 2019). ACL, 2019, pp. 165–176.
  - [3 ATTENTION TAXONOMY › 3.3 Query-Related Attention Mechanisms › 3.3.2 Multiplicity of Queries](#section-017)
- [97] Y. Zhou, R. Ji, J. Su, X. Sun, and W. Chen, “Dynamic capsule attention for visual question answering,” in 33rd AAAI Conference on Artificial Intelligence (AAAI 2019), vol. 33, no. 01. AAAI Press, 2019, pp. 9324–9331.
  - [3 ATTENTION TAXONOMY › 3.3 Query-Related Attention Mechanisms › 3.3.2 Multiplicity of Queries](#section-017)
- [98] Y. Wang, A. Sun, M. Huang, and X. Zhu, “Aspect-level sentiment analysis using AS-capsules,” in The World Wide Web Conference, 2019, pp. 2033–2044.
  - [3 ATTENTION TAXONOMY › 3.3 Query-Related Attention Mechanisms › 3.3.2 Multiplicity of Queries](#section-017)
- [99] Z. Dai, Z. Yang, Y. Yang, J. Carbonell, Q. Le, and R. Salakhutdinov, “Transformer-XL: Attentive language models beyond a fixedlength context,” in 57th Annual Meeting of the Association for Computational Linguistics (ACL 2019). ACL, 2019, pp. 2978–2988.
  - [3 ATTENTION TAXONOMY › 3.3 Query-Related Attention Mechanisms › 3.3.2 Multiplicity of Queries](#section-017)
- [100] N. Kitaev, Ł. Kaiser, and A. Levskaya, “Reformer: The efficient Transformer,” in 8th International Conference on Learning Representations (ICLR 2020), 2020.
  - [3 ATTENTION TAXONOMY › 3.3 Query-Related Attention Mechanisms › 3.3.2 Multiplicity of Queries](#section-017)
- [101] S. Wang, B. Li, M. Khabsa, H. Fang, and H. Ma, “Linformer: Selfattention with linear complexity,” arXiv:2006.04768, 2020.
  - [3 ATTENTION TAXONOMY › 3.3 Query-Related Attention Mechanisms › 3.3.2 Multiplicity of Queries](#section-017)
- [102] Z. Wu, Z. Liu, J. Lin, Y. Lin, and S. Han, “Lite transformer with long-short range attention,” in 8th International Conference on Learning Representations (ICLR 2020), 2020.
  - [3 ATTENTION TAXONOMY › 3.3 Query-Related Attention Mechanisms › 3.3.2 Multiplicity of Queries](#section-017)
- [103] Y. Tay, D. Bahri, D. Metzler, D.-C. Juan, Z. Zhao, and C. Zheng, “Synthesizer: Rethinking self-attention for transformer models,” in Proceedings of the 38th International Conference on Machine Learning (ICML 2021), vol. 139. PMLR, 2021, pp. 10 183–10 192.
  - [3 ATTENTION TAXONOMY › 3.3 Query-Related Attention Mechanisms › 3.3.2 Multiplicity of Queries](#section-017)
- [104] Y. Tay, M. Dehghani, D. Bahri, and D. Metzler, “Efficient transformers: A survey,” arXiv:2009.06732, 2020.
  - [3 ATTENTION TAXONOMY › 3.3 Query-Related Attention Mechanisms › 3.3.2 Multiplicity of Queries](#section-017)
- [105] X. Li, J. Song, L. Gao, X. Liu, W. Huang, X. He, and C. Gan, “Beyond RNNs: Positional self-attention with co-attention for video question answering,” in 33rd AAAI Conference on Artificial Intelligence (AAAI 2019), vol. 33. AAAI Press, 2019, pp. 8658– 8665.
  - [4 EVALUATION OF ATTENTION MODELS › 4.1 Extrinsic Evaluation](#section-019)；[4 EVALUATION OF ATTENTION MODELS › 4.2 Intrinsic Evaluation › 4.2.1 Evaluation via Human Attention](#section-021)
- [106] A. W. Yu, D. Dohan, M.-T. Luong, R. Zhao, K. Chen, M. Norouzi, and Q. V. Le, “QANet: Combining local convolution with global self-attention for reading comprehension,” in 6th International Conference on Learning Representations (ICLR 2018), 2018.
  - [4 EVALUATION OF ATTENTION MODELS › 4.2 Intrinsic Evaluation › 4.2.1 Evaluation via Human Attention](#section-021)
- [107] K. Papineni, S. Roukos, T. Ward, and W.-J. Zhu, “BLEU: a method for automatic evaluation of machine translation,” in 40th Annual Meeting of the Association for Computational Linguistics (ACL 2002). ACL, 2002, pp. 311–318.
  - [4 EVALUATION OF ATTENTION MODELS › 4.1 Extrinsic Evaluation](#section-019)
- [108] S. Banerjee and A. Lavie, “METEOR: An automatic metric for MT evaluation with improved correlation with human judgments,” in 2005 Workshop on Intrinsic and Extrinsic Evaluation Measures for Machine Translation and/or Summarization. ACL, 2005, pp. 65–72.
  - [4 EVALUATION OF ATTENTION MODELS › 4.1 Extrinsic Evaluation](#section-019)
- [109] R. Sennrich, “Perplexity minimization for translation model domain adaptation in statistical machine translation,” in 13th Conference of the European Chapter of the Association for Computational Linguistics (EACL 2012). ACL, 2012, pp. 539–549.
  - [4 EVALUATION OF ATTENTION MODELS › 4.1 Extrinsic Evaluation](#section-019)
- [110] M. Popovic and H. Ney, “Word error rates: Decomposition over´ POS classes and applications for error analysis,” in 2nd Workshop on Statistical Machine Translation (WMT 2007). ACL, 2007, pp. 48–55.
  - [4 EVALUATION OF ATTENTION MODELS › 4.1 Extrinsic Evaluation](#section-019)
- [111] P. Schwarz, P. Matejka, and J.ˇ Cernock<sup>ˇ</sup> y, “Towards lower error\` rates in phoneme recognition,” in 7th International Conference on Text, Speech and Dialogue (TSD 2004), ser. LNCS, vol. 3206. Springer, 2004, pp. 465–472.
  - [4 EVALUATION OF ATTENTION MODELS › 4.1 Extrinsic Evaluation](#section-019)
- [112] D. S. Turaga, Y. Chen, and J. Caviedes, “No reference PSNR estimation for compressed pictures,” Signal Processing: Image Communication, vol. 19, no. 2, pp. 173–184, 2004.
  - [4 EVALUATION OF ATTENTION MODELS › 4.1 Extrinsic Evaluation](#section-019)
- [113] P. Ndajah, H. Kikuchi, M. Yukawa, H. Watanabe, and S. Muramatsu, “SSIM image quality metric for denoised images,” in 3rd WSEAS International Conference on Visualization, Imaging and Simulation (VIS 2010). WSEAS, 2010, pp. 53–58.
  - [4 EVALUATION OF ATTENTION MODELS › 4.1 Extrinsic Evaluation](#section-019)
- [114] M. A. Rahman and Y. Wang, “Optimizing intersection-over-union in deep neural networks for image segmentation,” in 12th International Symposium on Visual Computing (ISVC 2016), ser. LNCS, vol. 10072. Springer, 2016, pp. 234–244.
  - [4 EVALUATION OF ATTENTION MODELS › 4.1 Extrinsic Evaluation](#section-019)
- [115] X. Chen, L. Yao, and Y. Zhang, “Residual attention U-net for automated multi-class segmentation of COVID-19 chest CT images,” arXiv:2004.05645, 2020.
  - [4 EVALUATION OF ATTENTION MODELS › 4.1 Extrinsic Evaluation](#section-019)
- [116] S. Liu, Y. Chen, K. Liu, and J. Zhao, “Exploiting argument information to improve event detection via supervised attention mechanisms,” in 55th Annual Meeting of the Association for Computational Linguistics (ACL 2017). ACL, 2017, pp. 1789–1798.
  - [4 EVALUATION OF ATTENTION MODELS › 4.2 Intrinsic Evaluation](#section-020)；[4 EVALUATION OF ATTENTION MODELS › 4.2 Intrinsic Evaluation › 4.2.1 Evaluation via Human Attention](#section-021)；[5 CONCLUSION](#section-023)
- [117] C. Liu, J. Mao, F. Sha, and A. Yuille, “Attention correctness in neural image captioning,” in 31st AAAI Conference on Artificial Intelligence (AAAI 2017). AAAI Press, 2017, pp. 4176–4182.
  - [4 EVALUATION OF ATTENTION MODELS › 4.2 Intrinsic Evaluation › 4.2.1 Evaluation via Human Attention](#section-021)；[5 CONCLUSION](#section-023)
- [118] A. Das, H. Agrawal, L. Zitnick, D. Parikh, and D. Batra, “Human attention in visual question answering: Do humans and deep networks look at the same regions?” Computer Vision and Image Understanding, vol. 163, pp. 90 – 100, 2017.
  - [4 EVALUATION OF ATTENTION MODELS › 4.2 Intrinsic Evaluation › 4.2.1 Evaluation via Human Attention](#section-021)
- [119] Y. Yu, J. Choi, Y. Kim, K. Yoo, S.-H. Lee, and G. Kim, “Supervising neural attention models for video captioning by human gaze data,” in 2017 IEEE Conference on Computer Vision and Pattern Recognition (CVPR 2017). IEEE Computer Society, 2017.
  - [4 EVALUATION OF ATTENTION MODELS › 4.2 Intrinsic Evaluation › 4.2.1 Evaluation via Human Attention](#section-021)；[5 CONCLUSION](#section-023)
- [120] S. Jain and B. C. Wallace, “Attention is not explanation,” in 2019 Conference of the North American Chapter of the Association for Computational Linguistics: Human Language Technologies (NAACL-HLT 2019). ACL, 2019, pp. 3543–3556.
  - [4 EVALUATION OF ATTENTION MODELS › 4.2 Intrinsic Evaluation › 4.2.2 Manual Evaluation](#section-022)
- [121] S. Wiegreffe and Y. Pinter, “Attention is not not explanation,” in 2019 Conference on Empirical Methods in Natural Language Processing and the 9th International Joint Conference on Natural Language Processing (EMNLP-IJCNLP 2019). ACL, 2019, pp. 11–20.
  - [4 EVALUATION OF ATTENTION MODELS › 4.2 Intrinsic Evaluation › 4.2.2 Manual Evaluation](#section-022)
- [122] A. K. Mohankumar, P. Nema, S. Narasimhan, M. M. Khapra, B. V. Srinivasan, and B. Ravindran, “Towards transparent and explainable attention models,” in 58th Annual Meeting of the Association for Computational Linguistics (ACL 2020). ACL, 2020, pp. 4206–4216.
  - [4 EVALUATION OF ATTENTION MODELS › 4.2 Intrinsic Evaluation › 4.2.2 Manual Evaluation](#section-022)
- [123] K. K. Thekumparampil, C. Wang, S. Oh, and L.-J. Li, “Attentionbased graph neural network for semi-supervised learning,” arXiv:1803.03735, 2018.
  - [5 CONCLUSION](#section-023)
- [124] D. Nie, Y. Gao, L. Wang, and D. Shen, “ASDNet: Attention based semi-supervised deep networks for medical image segmentation,” in 21st International Conference on Medical Image Computing and Computer-Assisted Intervention (MICCAI 2018), ser. LNCS, vol. 11073. Springer, 2018, pp. 370–378.
  - [5 CONCLUSION](#section-023)
- [125] Y. Alami Mejjati, C. Richardt, J. Tompkin, D. Cosker, and K. I. Kim, “Unsupervised attention-guided image-to-image translation,” in 32nd Annual Conference on Neural Information Processing Systems (NIPS 2018). Curran Associates, Inc., 2018, pp. 3693– 3703.
  - [5 CONCLUSION](#section-023)
- [126] R. He, W. S. Lee, H. T. Ng, and D. Dahlmeier, “An unsupervised neural attention model for aspect extraction,” in 55th Annual Meeting of the Associationfor Computational Linguistics (ACL 2017). ACL, 2017, pp. 388–397.
  - [5 CONCLUSION](#section-023)
