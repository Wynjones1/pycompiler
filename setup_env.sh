#!/usr/bin/env bash
OUTDIR=env
rm -Rf $OUTDIR
mkdir -p $OUTDIR
virtualenv $OUTDIR
cd $OUTDIR
source bin/activate
pip install pydot coverage
