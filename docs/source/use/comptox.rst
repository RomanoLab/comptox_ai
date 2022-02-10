.. _comptox:

************************
Computational Toxicology
************************

Computational toxicology is a field of research that has existed since roughly
the mid-1980s, but only in the past decade has it seen significant growth and
attention. Briefly, computational toxicology can be defined as *the use of
computational and informatics techniques to make discoveries regarding the
toxic effects of chemicals on organisms and the environment.* The term
*predictive toxicology* is often used synonymously with computational
toxicology.

Methods used in computational toxicology
****************************************

Before ComptoxAI, the set of computational tools available to toxicologists was
relatively limited. Let's review the most common of these with examples and
intuitive explanations:

Quantitative Structure-Activity Relationship (QSAR) modeling
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Quantitative structure-activity relationship (QSAR) modeling is the process of
building predictive models that accept structured descriptions of molecular
structure and predict a particular measure of activity. This predictive model
can be anything you want, but common choices include logistic regression,
random forests, support vector machines, and (increasingly) artificial neural
networks. The general form is:

.. math::

   \hat{y} = f(\mathbf{x}) + \epsilon

where :math:`\mathbf{x}` is a vector representing a chemical structure, 
:math:`\hat{y}` is a predicted activity value, :math:`\epsilon` is an arbitrary
error term, and :math:`f` is the predictive model.

Input features for a QSAR model are usually one of two types:

* **Fingerprints**: A sequence of binary features where each feature represents
  presence/absence of a particular structural characteristic. Some examples are
  whether the chemical contains an aromatic ring, a disulfide bond, has fewer
  than 3 oxygen atoms, etc. There are a number of different standardized 
  fingerprints, including MACCS, PubChem fingerprints, and others. We like to
  use MACCS, which has 166 binary features and tends to perform best on most of
  the tasks we have tested it on. MACCS fingerprints are available for every
  chemical in ComptoxAI.
* **Descriptors**: Continuous values characterizing a chemical structure,
  including molecular weight, log-p, number of aromatic rings, etc.

Depending on the predictive model you use, it is often effective to mix
fingerprints and molecular descriptors in the same analysis.

QSAR variations
"""""""""""""""

You'll often see other, similar terms used in place of QSAR. These usually aim
to more precisely desribe the type of activity being measured, but are all
mechanistically the same thing. For example:

* **QSPR** (Quantitative structure-property relationship) predicts a chemical
  property.
* **QSTR** (Quantitative structure-toxicity relationship) predicts a measure of
  toxicity.
* **QSBR** (Quantitative structure-biodegradability relationship) predicts rate
  of biodegradation.

For simplicity's sake, we usually just refer to everything as QSAR - it's a
good catch-all term.

Is QSAR quantitative?
"""""""""""""""""""""

Scientists sometimes argue about whether a QSAR analysis is truly quantitative
or if it instead is qualitative. E.g., when the predictive task is to determine
whether an assay is active or inactive, some researchers say that this outcome
is qualitative. We take the view that this is a dichotomous outcome that can be
represented as a binary (1/0 or True/False) variable, and is therefore
quantitative. If you are predicting a continuous quantity (e.g, lethal dose of
a chemical), this is clearly qunatitative no matter who you ask. But in the
end, we feel that the difference is minor and not worth worrying about
extensively.

Read-across
^^^^^^^^^^^

From a high level, read-across is a rather simple technique: To predict an
unknown property of interest in a certain chemical, you gather a list of
similar chemicals where the property is known, and extrapolate the likely value
of that property based on the distribution of that property in the related
chemicals. This can be done qualitatively (by simply assembling a table of
chemicals and visually 'reading across' the table to inspect patterns) or
quantitatively (by analyzing the trends in the property using statistical or
computational techniques). 

Read-across can be performed in a one-to-one, one-to-many, many-to-one, or
many-to-many fasion, depending on your available data and the other factors.
Additionally, you can determine the unknown value(s) by interpolation
(e.g., placing a chemical with a length-5 carbon chain between similar 
chemicals that have length-4 and length-6 carbon chains, and predicting a
property halfway between the two known values) or extrapolation.

Trend Analysis
^^^^^^^^^^^^^^

Trend analysis is similar to QSAR, but rather than predicting activity, you
instead collect a group of chemicals already known to have a certain type of
activity and build a predictive model that estimates trends in a chemical
property of interest. For example, you can use trend analysis to predict the
binding affinity of aryl hydrocarbon receptor agonists to the AHR protein. To
do this, you need to (a.) already have a set of chemicals known to bind to AHR,
and (b.) have binding affinities for a subset of those chemicals that are used
to build the predictive model. The trained model is used to "fill in the gaps"
for unknown binding affinity measurements.

Adverse Outcome Pathways
************************

Adverse Outcome Pathways (AOPs) are a central concept in modern applications of
computational toxicology (and, by extension, ComptoxAI). For more information,
please refer to our complete guide of AOPs :ref:`here <aop>`.

Major research initiatives in computational toxicology
******************************************************

Tox21
^^^^^

The Toxicology in the 21st Century (Tox21) consortium was formed by the US EPA,
NTP, NCATS, and FDA to provide high-throughput screening resources and new
cellular models for predictive toxicology. Currently, one of their main
research outputs is a dataset consisting of 72 toxicology-focused assays
evaluated on up to ~8,000 chemicals of interest, with new data being added over
time. We use these data in ComptoxAI to represent assays and known activity
values for chemicals in ComptoxAI's knowledge base. 

AOP-Wiki / AOP-DB / SAAOP
^^^^^^^^^^^^^^^^^^^^^^^^^

The Society for the Advancement of Adverse Outcome Pathways (SAAOP) is
dedicated to assembling data resources and rich information regarding known
AOPs (click here for more info on what AOPs are). One of the main resources
they maintain is the AOP-Wiki, which provides an interface for experts to share
manually-annotated AOP data with the larger scientific community. The AOP-Wiki
maintainers manually link key events, stressors, adverse outcomes, and adverse
outcome relationships to controlled terms, which allow researchers to assemble
larger networks of overlapping AOPs. When researchers submit AOPs, they can be
tracked along the different stages of their development, and are only marked as
endorsed or approved once they have passed community review. Contents of the
AOP-Wiki are available for download, and are used to reconstruct key event
relationships in ComptoxAI's knowledge base (which are currently not present in
the larger AOP-DB resource).