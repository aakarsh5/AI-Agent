import { ModeToggle } from "@/components/theme-toggle";
import { Button } from "@/components/ui/button";
export default function Home() {
  return (
    <>
      <ModeToggle />
      <h1>Home Page</h1>
      <Button>Click me</Button>
    </>
  );
}
