# Method Report for Polaris ASAP Antiviral Ligand Poses 2025 Challenge - ****WORK IN PROGRESS****

stand by, still writing this up, my approach was very brain-dead so it probably doesn't matter very much, but I'd at least like to say enough here to get my (terrible) submission scored

tl;dr I'm a total novice at this, so I decided to try the simplest thing I possibly could.  I bet I'm gonna come in last, but that's OK, because this was incredibly fun and interesting.

## Constraints
- *Time*:  I started in earnest about a week before the original competition deadline.
- *Cluelessness*:
- *Open-source only*:  No commercial licenses for me.

## Approach
I chose [gnina](https://github.com/gnina/gnina) (v1.3 master:97fa6bc+) because it's free, open-source, and relatively easy to set up.  I figured I didn't the time or expertise to build and train my own model from the ground up, so I wound up not using the training data for anything but a little EDA.  This seemed bonkers to me, but I'd seen that another user on the competition Discord channel had gotten decent results without doing their own training.  The clock was ticking, so I just rolled with it.

I ran `gnina` twice against the test set, using the provided reference structures (`data/raw/reference_structures/MERS-CoV-Mpro/protein.pdb` and `data/raw/reference_structures/SARS-CoV-2-Mpro/protein.pdb`), and setting `--autobox-ligand` to the corresponding `ligand.sdf`.  The only difference between the runs was that one used `--exhaustiveness 16` and the other `--exhaustiveness 64`.  All other settings were left on the `gnina` defaults.

From each run, for each ligand, I pulled the top-performing pose by `CNNScore`.  To choose the final pose for submission:

- Choose the pose with the higher `<CNNScore>` from the two runs.
- If the `<CNNScore>`s are close (within 0.05), choose the pose with higher `<CNN_VS>`.
- If the `<CNNScore>`s are close *and* the RMSD between the two poses is big (> 5Å), go with the `--exhaustiveness 64` pose, on the assumption that maybe a more-exhaustive search was likelier to find something good.  This is unsatisfying, but you've gotta choose something.

After prototyping locally, I ran all workflows on a GCP Ubuntu 24.04 box with a Tesla G4 GPU.
