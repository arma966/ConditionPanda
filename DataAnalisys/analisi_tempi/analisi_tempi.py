import numpy as np
import matplotlib.pyplot as plt
import statsmodels.stats.power as smp
import seaborn as sns
import pandas as pd


def compare_two_distributions(two_point, n1, n2):
    fig2 = plt.figure(2)
    x_start = two_point[0, n1] - 2
    x_end = two_point[0, n2] + 2
    x = np.linspace(x_start, x_end, num=500)

    mu1 = two_point[0, n1]
    sigma1 = two_point[1, n1]

    mu2 = two_point[0, n2]
    sigma2 = two_point[1, n2]

    y1 = (
        1
        / (sigma1 * np.sqrt(2 * np.pi))
        * np.exp(-((x - mu1) ** 2) / (2 * sigma1 ** 2))
    )
    y2 = (
        1
        / (sigma2 * np.sqrt(2 * np.pi))
        * np.exp(-((x - mu2) ** 2) / (2 * sigma2 ** 2))
    )

    ax2 = fig2.gca()
    ax2.plot(x, y1, label="distribution %s" % n1)
    ax2.plot(x, y2, label="distribution %s" % n2)
    ax2.set(
        xlabel="time [s]",
        ylabel="pdf estimation",
        title="Sample %s vs sample %s" % (n1, n2),
    )
    ax2.legend()


"""-----------------------------Data generation-----------------------------"""
# Generate 10 normal distribution
n_distributions = 10
n_samples = 14
means = np.ones(n_distributions) * 5 + np.arange(n_distributions) * 0.1
scale = np.ones(n_distributions) * 0.5

array_distribution = np.random.normal(means, scale, size=(n_samples, n_distributions))
two_point = np.zeros((2, n_distributions))

for i in range(n_distributions):
    two_point[0, i] = np.mean(array_distribution[:, i])
    two_point[1, i] = np.std(array_distribution[:, i]) / np.sqrt(n_samples)

a = two_point

result_list = []
for i in range(1, array_distribution.shape[1]):
    es = (two_point[0, 0] - two_point[0, i]) / (two_point[0, 1] / n_samples ** (0.5))

    result = smp.tt_ind_solve_power(
        effect_size=es,
        nobs1=n_samples,
        power=0.8,
        ratio=1.0,
        alternative="smaller",
        alpha=None,
    )
    result_list.append(result)

"""-----------------------Box plot of generated data-----------------------"""
fig1 = plt.figure(1)
ax1 = fig1.gca()
ax1.boxplot(array_distribution)
ax1.set(xlabel="N° block", ylabel="time [s]")


#%%
""" Plot the mean time of the blocks with a confidence interval ci = 0.95 """

x = (
    (np.ones((n_samples, n_distributions)) * np.arange(n_distributions))
    .transpose()
    .reshape((1, n_distributions * n_samples))[0, :]
)
y = array_distribution.transpose().reshape(1, n_distributions * n_samples)[0, :]
data = np.vstack((x, y)).transpose()

df = pd.DataFrame(data=data, index=None, columns=["N° block", "Time [s]"])
fig3 = plt.figure(3)
ax3 = fig3.gca()
ax3 = sns.lineplot(data=df, x="N° block", y="Time [s]")

#%%
"""-----------Compare two estimated pdf, given the blocks number-----------"""

distribution1 = 9
distribution2 = 1
compare_two_distributions(two_point, distribution1, distribution2)

mu1 = np.round(two_point[0, distribution1], 2)
mu2 = np.round(two_point[0, distribution2], 2)
print("Block %s: mu = %s s" % (distribution1, mu1))
print("Block %s: mu = %s s" % (distribution2, mu2))
