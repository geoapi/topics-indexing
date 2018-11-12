from __future__ import unicode_literals, print_function

import plac
import random
from pathlib import Path
import spacy
from spacy.util import minibatch, compounding


# new entity label
LABEL = 'APINAME'

# training data
# Note: If you're using an existing model, make sure to mix in examples of
# other entity types that spaCy correctly recognized before. Otherwise, your
# model might learn the new type, but "forget" what it previously knew.
# https://explosion.ai/blog/pseudo-rehearsal-catastrophic-forgetting
TRAIN_DATA = [
    ("Winapi is a structured API for fetching objects.", {
        'entities': [(0, 6, 'APINAME')]
    }),

    ("The Winapi (formerly called the Win32 API) is the core set of application programming interfaces available for the Microsoft Windows operating systems.", {
        'entities': [(4, 10, 'APINAME')]
    }),

    ("Winapi is amongst  variety of APIs, mostly windows apis for developers.", {
        'entities': [(0, 6, 'APINAME')]
    }),

    ("You can pick winapi which is for windows", {
        'entities': [(13, 19, 'APINAME')]
    })
    #,
    #
    # ("ASP.NET Web API is a framework for building HTTP services for clients like browsers and mobile devices. It is based on the Microsoft .NET Framework and an ideal choice for building RESTful services", {
    #     'entities': [(0, 14, 'API')]
    # }),
    # ("The Instagram API enables the integration of Instagram\'s photos\\videos content and functionality into a website, application or a device. Tag specific questions about the use of Instagram API", {
    #     'entities': [(4, 17, 'API')]
    # }),
    # ("Use the Gmail API to add Gmail features to your app. RESTful access to threads, messages, labels, drafts and history. Easy to use from modern web languages.", {
    #     'entities': [(8, 17, 'API')]
    # })
]


@plac.annotations(
    model=("Model name. Defaults to blank 'en' model.", "option", "m", str),
    new_model_name=("New model name for model meta.", "option", "nm", str),
    output_dir=("Optional output directory", "option", "o", Path),
    n_iter=("Number of training iterations", "option", "n", int))
def main(model=None, new_model_name='api', output_dir=None, n_iter=10):
    """Set up the pipeline and entity recognizer, and train the new entity."""

    if model is not None:
        nlp = spacy.load(model)  # load existing spaCy model
        print("Loaded model '%s'" % model)
    else:
        nlp = spacy.blank('en')  # create blank Language class
        print("Created blank 'en' model")
    # Add entity recognizer to model if it's not in the pipeline
    # nlp.create_pipe works for built-ins that are registered with spaCy
    if 'ner' not in nlp.pipe_names:
        ner = nlp.create_pipe('ner')
        nlp.add_pipe(ner)
    # otherwise, get it, so we can add labels to it
    else:
        ner = nlp.get_pipe('ner')

    ner.add_label(LABEL)   # add new entity label to entity recognizer
    if model is None:
        nlp.vocab.vectors.name = 'spacy_pretrained_vectors'
        optimizer = nlp.begin_training()
    else:
        # Note that 'begin_training' initializes the models, so it'll zero out
        # existing entity types.
        optimizer = nlp.entity.create_optimizer()

# Define the NER name

    # get names of other pipes to disable them during training
    other_pipes = [pipe for pipe in nlp.pipe_names if pipe != 'ner']
    with nlp.disable_pipes(*other_pipes):  # only train NER
        for itn in range(n_iter):
            random.shuffle(TRAIN_DATA)
            losses = {}
            # batch up the examples using spaCy's minibatch
            batches = minibatch(TRAIN_DATA, size=compounding(4., 32., 1.001))
            for batch in batches:
                texts, annotations = zip(*batch)
                nlp.update(texts, annotations, sgd=optimizer, drop=0.35,
                           losses=losses)
            print('Losses', losses)

    # test the trained model
    test_text = 'pick Winapi or facebookgraphapi ?'
    doc = nlp(test_text)
    print("Entities in '%s'" % test_text)
    for ent in doc.ents:
        print(ent.label_, ent.text)

    # save model to output directory
    if output_dir is not None:
        output_dir = Path(output_dir)
        if not output_dir.exists():
            output_dir.mkdir()
        nlp.meta['name'] = new_model_name  # rename model
        nlp.to_disk(output_dir)
        print("Saved model to", output_dir)

        # test the saved model
        print("Loading from", output_dir)
        nlp2 = spacy.load(output_dir)
        doc2 = nlp2(test_text)
        for ent in doc2.ents:
            print(ent.label_, ent.text)


if __name__ == '__main__':
    plac.call(main)
