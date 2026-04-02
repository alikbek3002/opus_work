import { motion } from 'framer-motion';
import { TariffPlan } from '../../lib/api';

interface PricingProps {
  tariffs: TariffPlan[];
  onSelect: (id: string) => void;
  isPopularIndex?: number;
  loadingTariffId?: string | null;
}

interface PricingCardProps {
  label: string;
  price: number;
  oldPrice?: number;
  description: string;
  contactsLine: string;
  dailyLimitLine?: string;
  durationLine: string;
  cta: string;
  background: string;
  BGComponent: React.FC;
  onSelect: () => void;
  isPopular: boolean;
  isLoading: boolean;
}

export const SquishyPricing = ({ tariffs, onSelect, isPopularIndex = 1, loadingTariffId = null }: PricingProps) => {
  const getThemeByTariff = (tariff: TariffPlan, index: number) => {
    if (tariff.period === "day") {
      return {
        bgColor: "bg-amber-500 dark:bg-amber-600",
        bgComponent: BGComponent3,
      };
    }
    if (tariff.period === "week") {
      return {
        bgColor: "bg-emerald-500 dark:bg-emerald-600",
        bgComponent: BGComponent2,
      };
    }
    if (tariff.period === "month") {
      return {
        bgColor: "bg-indigo-500 dark:bg-indigo-600",
        bgComponent: BGComponent1,
      };
    }
    if (tariff.period === "quarter") {
      return {
        bgColor: "bg-red-600 dark:bg-red-700",
        bgComponent: BGComponent1,
      };
    }

    const backgroundComponents = [BGComponent1, BGComponent2, BGComponent3];
    const backgroundColors = [
      "bg-indigo-500 dark:bg-indigo-600",
      "bg-purple-500 dark:bg-purple-600",
      "bg-pink-500 dark:bg-pink-600",
    ];
    return {
      bgColor: backgroundColors[index % backgroundColors.length],
      bgComponent: backgroundComponents[index % backgroundComponents.length],
    };
  };

  const getOldPrice = (tariff: TariffPlan) => {
    if (tariff.period === "week") return 2900;
    if (tariff.period === "month") return 6900;
    if (tariff.period === "quarter") return 19900;
    return undefined;
  };

  const getDurationLine = (tariff: TariffPlan) => {
    if (tariff.period === "day") return "на 1 день";
    if (tariff.period === "week") return "на 7 дней";
    if (tariff.period === "month") return "на 30 дней";
    if (tariff.period === "quarter") return "на 90 дней";
    return `на ${tariff.period}`;
  };

  const getDailyLimitLine = (tariff: TariffPlan) => {
    if (tariff.period === "day") return "лимит: 3 контакта/день";
    if (tariff.period === "week") return "лимит: 15 контактов/день";
    if (tariff.period === "month") return "лимит: 20 контактов/день";
    if (tariff.period === "quarter") return "лимит: 15 контактов/день";
    return undefined;
  };

  return (
    <section className="bg-background px-4 py-12 transition-colors">
      <div className="mx-auto flex w-fit flex-wrap justify-center gap-6 md:gap-8">
        {tariffs.map((tariff: TariffPlan, index: number) => {
          const { bgColor, bgComponent } = getThemeByTariff(tariff, index);

          return (
            <PricingCard
              key={tariff.id}
              label={tariff.name}
              price={tariff.price}
              oldPrice={getOldPrice(tariff)}
              contactsLine={`${tariff.card_limit} контактов`}
              dailyLimitLine={getDailyLimitLine(tariff)}
              durationLine={getDurationLine(tariff)}
              description={
                tariff.description
                  ? tariff.description
                  : `Доступ к базе проверенных кандидатов. Лимит карточек: ${tariff.card_limit}`
              }
              cta="Выбрать тариф"
              background={bgColor}
              BGComponent={bgComponent}
              onSelect={() => onSelect(tariff.id)}
              isPopular={index === isPopularIndex}
              isLoading={loadingTariffId === tariff.id}
            />
          );
        })}
      </div>
    </section>
  );
};

const PricingCard = ({
  label,
  price,
  oldPrice,
  description,
  contactsLine,
  dailyLimitLine,
  durationLine,
  cta,
  background,
  BGComponent,
  onSelect,
  isPopular,
  isLoading,
}: PricingCardProps) => {
  return (
    <motion.div
      whileHover="hover"
      transition={{ duration: 1, ease: "backInOut" }}
      variants={{ hover: { scale: 1.05 } }}
      className={`relative h-96 w-80 shrink-0 overflow-hidden rounded-xl p-8 ${background} shadow-lg hover:shadow-xl transition-shadow ${isPopular ? 'ring-4 ring-primary ring-offset-2 ring-offset-background' : ''}`}
    >
      {isPopular && (
        <div className="absolute top-0 right-0 bg-primary text-primary-foreground px-3 py-1 text-xs font-bold rounded-bl-lg z-20 shadow-md">
          Популярный
        </div>
      )}
      <div className="relative z-10 text-white h-full flex flex-col">
        <span className="mb-3 block w-fit rounded-full bg-white/20 backdrop-blur-sm px-3 py-0.5 text-sm font-medium text-white border border-white/20">
          {label}
        </span>
        <div className="my-2 flex items-end gap-2 origin-top-left">
          <motion.span
            initial={{ scale: 0.85 }}
            variants={{ hover: { scale: 1 } }}
            transition={{ duration: 1, ease: "backInOut" }}
            className="font-mono text-5xl font-black leading-[1.2]"
          >
            {price.toLocaleString()} сом
          </motion.span>
          {oldPrice && (
            <span className="font-mono text-xl line-through text-white/50 mb-1">
              {oldPrice.toLocaleString()} сом
            </span>
          )}
        </div>
        <div className="mt-4 rounded-2xl border border-white/20 bg-white/12 p-4 backdrop-blur-sm">
          <div className="text-lg font-black tracking-tight text-white">{contactsLine}</div>
          {dailyLimitLine ? (
            <div className="mt-1 text-sm font-medium text-white/85">{dailyLimitLine}</div>
          ) : null}
          <div className="mt-1 text-sm font-medium text-white/85">{durationLine}</div>
        </div>
        <p className="mt-4 text-sm leading-6 text-white/90 flex-grow">{description}</p>
      </div>
      <button
        onClick={onSelect}
        disabled={isLoading}
        className="absolute bottom-4 left-4 right-4 z-20 inline-flex items-center justify-center gap-2 rounded-lg border-2 border-white bg-white py-2 text-center font-mono font-black uppercase text-neutral-800 backdrop-blur-sm transition-all duration-200 hover:bg-white/10 hover:text-white hover:border-white/80 focus:outline-none focus:ring-2 focus:ring-white/50 focus:ring-offset-2 focus:ring-offset-transparent disabled:cursor-wait disabled:bg-white/85 disabled:text-neutral-700 disabled:hover:border-white"
      >
        {isLoading ? (
          <>
            <span className="h-4 w-4 animate-spin rounded-full border-2 border-neutral-400 border-t-neutral-800" />
            Генерируем оплату...
          </>
        ) : (
          cta
        )}
      </button>
      <BGComponent />
    </motion.div>
  );
};

const BGComponent1 = () => (
  <motion.svg
    width="320"
    height="384"
    viewBox="0 0 320 384"
    fill="none"
    xmlns="http://www.w3.org/2000/svg"
    variants={{ hover: { scale: 1.5 } }}
    transition={{ duration: 1, ease: "backInOut" }}
    className="absolute inset-0 z-0"
  >
    <motion.circle
      variants={{ hover: { scaleY: 0.5, y: -25 } }}
      transition={{ duration: 1, ease: "backInOut", delay: 0.2 }}
      cx="160.5"
      cy="114.5"
      r="101.5"
      fill="rgba(0, 0, 0, 0.2)"
      className="dark:fill-white/10"
    />
    <motion.ellipse
      variants={{ hover: { scaleY: 2.25, y: -25 } }}
      transition={{ duration: 1, ease: "backInOut", delay: 0.2 }}
      cx="160.5"
      cy="265.5"
      rx="101.5"
      ry="43.5"
      fill="rgba(0, 0, 0, 0.2)"
      className="dark:fill-white/10"
    />
  </motion.svg>
);

const BGComponent2 = () => (
  <motion.svg
    width="320"
    height="384"
    viewBox="0 0 320 384"
    fill="none"
    xmlns="http://www.w3.org/2000/svg"
    variants={{ hover: { scale: 1.05 } }}
    transition={{ duration: 1, ease: "backInOut" }}
    className="absolute inset-0 z-0"
  >
    <motion.rect
      x="14"
      width="153"
      height="153"
      rx="15"
      fill="rgba(0, 0, 0, 0.2)"
      className="dark:fill-white/10"
      variants={{ hover: { y: 219, rotate: "90deg", scaleX: 2 } }}
      style={{ y: 12 }}
      transition={{ delay: 0.2, duration: 1, ease: "backInOut" }}
    />
    <motion.rect
      x="155"
      width="153"
      height="153"
      rx="15"
      fill="rgba(0, 0, 0, 0.2)"
      className="dark:fill-white/10"
      variants={{ hover: { y: 12, rotate: "90deg", scaleX: 2 } }}
      style={{ y: 219 }}
      transition={{ delay: 0.2, duration: 1, ease: "backInOut" }}
    />
  </motion.svg>
);

const BGComponent3 = () => (
  <motion.svg
    width="320"
    height="384"
    viewBox="0 0 320 384"
    fill="none"
    xmlns="http://www.w3.org/2000/svg"
    variants={{ hover: { scale: 1.25 } }}
    transition={{ duration: 1, ease: "backInOut" }}
    className="absolute inset-0 z-0"
  >
    <motion.path
      variants={{ hover: { y: -50 } }}
      transition={{ delay: 0.3, duration: 1, ease: "backInOut" }}
      d="M148.893 157.531C154.751 151.673 164.249 151.673 170.107 157.531L267.393 254.818C273.251 260.676 273.251 270.173 267.393 276.031L218.75 324.674C186.027 357.397 132.973 357.397 100.25 324.674L51.6068 276.031C45.7489 270.173 45.7489 260.676 51.6068 254.818L148.893 157.531Z"
      fill="rgba(0, 0, 0, 0.2)"
      className="dark:fill-white/10"
    />
    <motion.path
      variants={{ hover: { y: -50 } }}
      transition={{ delay: 0.2, duration: 1, ease: "backInOut" }}
      d="M148.893 99.069C154.751 93.2111 164.249 93.2111 170.107 99.069L267.393 196.356C273.251 202.213 273.251 211.711 267.393 217.569L218.75 266.212C186.027 298.935 132.973 298.935 100.25 266.212L51.6068 217.569C45.7489 211.711 45.7489 202.213 51.6068 196.356L148.893 99.069Z"
      fill="rgba(0, 0, 0, 0.2)"
      className="dark:fill-white/10"
    />
    <motion.path
      variants={{ hover: { y: -50 } }}
      transition={{ delay: 0.1, duration: 1, ease: "backInOut" }}
      d="M148.893 40.6066C154.751 34.7487 164.249 34.7487 170.107 40.6066L267.393 137.893C273.251 143.751 273.251 153.249 267.393 159.106L218.75 207.75C186.027 240.473 132.973 240.473 100.25 207.75L51.6068 159.106C45.7489 153.249 45.7489 143.751 51.6068 137.893L148.893 40.6066Z"
      fill="rgba(0, 0, 0, 0.2)"
      className="dark:fill-white/10"
    />
  </motion.svg>
);
